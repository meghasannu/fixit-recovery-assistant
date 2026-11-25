from fastapi.testclient import TestClient

from app.diffing import diff_words
from app.main import app
from app.mock_data import CANNED_REVISIONS, SAMPLES
from app.prompts import REVISIONS, build_revision_context

client = TestClient(app)
TECH = next(s for s in SAMPLES if s["id"] == "too-technical")


def _revise(**extra):
    body = {"source_text": TECH["source"], "mode": "summarise",
            "request": TECH["request"], "current_answer": TECH["bad_output"]}
    body.update(extra)
    return client.post("/api/revise", json=body)


def test_controls_match_prompt_specification():
    controls = client.get("/api/controls").json()
    assert [c["id"] for c in controls] == list(REVISIONS)
    assert all(c["hint"] for c in controls)


def test_button_returns_revision_and_code_computed_changes():
    res = _revise(button="simpler")
    assert res.status_code == 200
    data = res.json()
    assert data["output"] == CANNED_REVISIONS[("too-technical", "simpler")]
    assert data["action"] == "Simpler"
    report = data["changes"]["report"]
    assert report["words_before"] == len(TECH["bad_output"].split())
    assert report["words_after"] == len(data["output"].split())
    # Rebuilding the new text from the highlight segments gives the output.
    rebuilt = "".join(s["text"] for s in data["changes"]["segments"] if s["type"] != "del")
    assert rebuilt == data["output"]


def test_free_text_correction_is_sent_as_information():
    res = _revise(correction="Mention that plants release oxygen")
    assert res.status_code == 200
    sent = res.json()["sent"]["user"]
    assert "<correction>\nMention that plants release oxygen\n</correction>" in sent
    assert res.json()["action"] == "Your correction"


def test_needs_exactly_one_of_button_or_correction():
    assert _revise().status_code == 422
    assert _revise(button="shorter", correction="also this").status_code == 422


def test_unknown_button_is_rejected():
    assert _revise(button="make-it-perfect").status_code == 422


def test_mock_fallback_is_always_labelled():
    res = client.post("/api/revise", json={
        "source_text": "First point. Second point. Third point.",
        "current_answer": "First point. Second point.",
        "button": "shorter",
    })
    assert res.json()["output"].startswith("[Mock response]")


def test_revision_prompt_keeps_answer_and_source_tagged():
    ctx = build_revision_context("summarise", "SRC", "REQ", "ANS", button="shorter")
    assert "<source>\nSRC\n</source>" in ctx["user"]
    assert "<current_answer>\nANS\n</current_answer>" in ctx["user"]
    assert REVISIONS["shorter"]["instruction"] in ctx["user"]


def test_diff_counts_added_and_removed_words():
    d = diff_words("The cat sat on the mat.", "The black cat sat on a mat.")
    r = d["report"]
    assert (r["words_before"], r["words_after"]) == (6, 7)
    assert (r["words_added"], r["words_removed"]) == (2, 1)
    assert not r["unchanged"]


def test_diff_reports_unchanged_text():
    assert diff_words("Same text.", "Same text.")["report"]["unchanged"] is True


def test_scripted_own_words_correction_in_mock_mode():
    res = _revise(correction="Use plain words and mention that plants release oxygen")
    from app.mock_data import CANNED_CORRECTIONS
    assert res.json()["output"] == CANNED_CORRECTIONS["too-technical"]["output"]
