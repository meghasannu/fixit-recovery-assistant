"""Model clients: a real Gemini client and a deterministic mock.

Both share one interface, generate(context) -> str, so the rest of the app does
not care which one is running. The mock makes the prototype runnable and
repeatable without a key (labelled 'Simulated' in the report).
"""

import json
import re
import time

from . import config
from .checks import _content_words, _stem
from .mock_data import AUTOFIX, CANNED_CORRECTIONS, CANNED_REVISIONS, find_sample


class LLMError(Exception):
    """Raised when the model call fails; shown to the user as a clear error."""


class MockClient:
    """Deterministic stand-in for the model (labelled 'Simulated').

    Seeded demo cases return scripted answers so storyboards are repeatable.
    Any other input gets a simple transformation, always prefixed
    "[Mock response]" so it can never be mistaken for a real model answer.
    """

    name = "mock"

    def generate(self, context: dict, *, source_text: str = "",
                 revision: dict | None = None, request: str = "",
                 json_mode: bool = False) -> str:
        # Simulated latency so the waiting feedback behaves as it would live.
        time.sleep(config.MOCK_DELAY_MS / 1000)
        sample = find_sample(source_text)
        if json_mode:
            return self._autofix(sample, request)
        if revision is None:
            if sample:
                # The demo's original request reproduces its bad first answer;
                # any other request (e.g. an approved Auto-fix rewrite) gets the
                # scripted better answer.
                if request.strip() and request.strip() != sample["request"].strip():
                    return AUTOFIX[sample["id"]]["output"]
                return sample["bad_output"]
            return f"[Mock response] {_first_sentences(source_text, 3)}".strip()
        return self._revise(sample, source_text, revision)

    def _autofix(self, sample, request: str) -> str:
        if sample:
            return json.dumps(AUTOFIX[sample["id"]]["proposal"])
        base = request.strip() or "Summarise this."
        return json.dumps({
            "diagnosis": "[Mock] A real model would name the main problem here.",
            "rewritten_request": f"{base} Write about 100 words in plain language "
                                 f"for a first-year student and cover the main points.",
            "changes": ["Added: about 100 words.", "Added: plain language.",
                        "Added: cover the main points."],
            "assumptions": ["Reader is a first-year student."],
        })

    def _revise(self, sample, source_text: str, revision: dict) -> str:
        button = revision.get("button")
        current = _strip_mock_label(revision.get("current", ""))
        if sample and button and (sample["id"], button) in CANNED_REVISIONS:
            return CANNED_REVISIONS[(sample["id"], button)]
        source_sents = _sentences(source_text)
        current_sents = _sentences(current)
        if button == "shorter":
            keep = max(1, len(current_sents) // 2)
            text = " ".join(current_sents[:keep])
        elif button == "simpler":
            text = _first_sentences(source_text, 3)
        elif button == "example":
            text = current + " (A mock answer would add an example from the source here.)"
        elif button in ("detail", "missing"):
            extra = next((s for s in source_sents if s not in current), "")
            text = f"{current} {extra}".strip()
        else:  # free-text correction
            correction = revision.get("correction", "").strip()
            absent = _absent_from_source(correction, source_text, current)
            if absent:
                # Decline repair turn (L07): say what the source lacks instead
                # of inventing it (sycophancy, L08).
                return (f"{current}\n\nYour text does not mention "
                        f"{', '.join(absent)}, so FixIt has not added it.")
            scripted = CANNED_CORRECTIONS.get(sample["id"]) if sample else None
            if scripted and all(k in correction.lower() for k in scripted["keywords"]):
                return scripted["output"]
            text = (f"{current} (A mock answer would apply your correction "
                    f"here: \"{correction}\".)")
        return f"[Mock response] {text}".strip()


def _absent_from_source(correction: str, source: str, current: str) -> list[str]:
    """Content words of a correction found in neither the source nor the answer.

    Instruction words such as 'mention' or 'remove' are ignored; only words
    that name content count.
    """
    known = {_stem(w) for w in _content_words(source + " " + current)}
    instruction = {"mention", "include", "remove", "delete", "change", "please",
                   "explain", "describe", "words", "sentence", "sentences",
                   "shorter", "longer", "simpler", "clearer", "should", "answer"}
    return [f"“{w}”" for w in sorted(_content_words(correction))
            if len(w) >= 5 and w not in instruction and _stem(w) not in known]


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def _first_sentences(text: str, n: int) -> str:
    return " ".join(_sentences(text)[:n])


def _strip_mock_label(text: str) -> str:
    return text.removeprefix("[Mock response]").strip()


class GeminiClient:
    def __init__(self, api_key: str, model: str):
        from google import genai  # imported here so mock mode needs no SDK setup

        self._genai = genai
        self._client = genai.Client(api_key=api_key)
        self.name = model

    def generate(self, context: dict, *, source_text: str = "",
                 revision: dict | None = None, request: str = "",
                 json_mode: bool = False) -> str:
        types = self._genai.types
        settings = {"system_instruction": context["system"]}
        if json_mode:
            settings["response_mime_type"] = "application/json"
        # Retry briefly when the service is busy or rate-limited: these errors
        # are usually temporary (seen in live testing as "503 UNAVAILABLE").
        # Other errors (bad key, wrong model name) are not retried.
        attempts = 1 + len(RETRY_DELAYS)
        for attempt in range(attempts):
            try:
                response = self._client.models.generate_content(
                    model=self.name,
                    contents=context["user"],
                    config=types.GenerateContentConfig(**settings),
                )
                break
            except Exception as exc:  # network, quota, auth or model-name errors
                if _is_temporary(exc) and attempt < attempts - 1:
                    time.sleep(RETRY_DELAYS[attempt])
                    continue
                raise LLMError(_friendly(exc)) from exc
        text = (response.text or "").strip()
        if not text:
            raise LLMError("The model returned an empty response.")
        return text


RETRY_DELAYS = (2, 5)  # seconds to wait before the 2nd and 3rd attempt


def _is_temporary(exc: Exception) -> bool:
    text = str(exc)
    return any(k in text for k in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED",
                                   "overloaded", "high demand"))


def _friendly(exc: Exception) -> str:
    """A message the person can act on, instead of a raw error dump."""
    text = str(exc)
    if "503" in text or "UNAVAILABLE" in text or "high demand" in text:
        return "Google's model is busy right now (high demand)."
    if "429" in text or "RESOURCE_EXHAUSTED" in text:
        return "The free usage limit was reached. Wait a minute and try again."
    if "API key" in text or "API_KEY" in text or "401" in text or "403" in text:
        return "The Gemini API key was not accepted. Check GEMINI_API_KEY in .env."
    if "404" in text or "not found" in text.lower():
        return "The model name was not found. Check GEMINI_MODEL in .env."
    return f"The model call failed: {text[:200]}"


def get_client():
    if config.MOCK_MODE:
        return MockClient()
    return GeminiClient(config.GEMINI_API_KEY, config.GEMINI_MODEL)
