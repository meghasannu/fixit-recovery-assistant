# FixIt: an error-recovery assistant for AI summaries

Prose word count: 859 words (code and commands excluded).

FixIt is a web prototype that helps a student recover when an AI-generated
summary or explanation misses the mark. It is the Assignment 2 project for
Intelligent Interactive Systems (University of Birmingham). The report
explains the design; this README explains how to inspect it.

## Project status

**Implemented**

* Paste a reading, choose Summarise or Explain, state what you need, get an
answer from Google Gemini.
* Three recovery routes: five correction buttons (Shorter, Simpler, Add
example, More detail, Fix missing point) with a preview of each effect;
free-text correction; Auto-fix, which proposes a rewritten request with its
diagnosis, changes and assumptions and runs only after approval.
* "FixIt noticed": checks in code suggest a likely fix but never apply one.
* New words highlighted; change report computed by code; version history with
authorship labels; undo that never deletes.
* Declines corrections that ask for facts missing from the source.
* Step path, "How FixIt works" panel (including what it can't do), copy,
keyboard shortcuts, accessibility pass.
* "This answer works for me" with a session summary and a downloadable JSON
log of counts and timings (no text is logged or stored).
* 52 automated tests; a live prompt test runner (8 cases, 13 criteria; 13 of 13
passed on 2026-11-16).

**Simulated**

* Mock mode (no API key): scripted responses, labelled in the interface.
* Three seeded demonstration failures. An unchanged demo case always starts
from its scripted bad answer, labelled "Seeded demo failure, not written by
the model"; with a key, every later step uses the live model.

**Unfinished (planned)**

* AI-generated correction controls; sentence-to-source links; the
three-condition user study from Assignment 1 (the session log is built for
it, but no participants have been tested).

## Technology stack

|Part|Choice|What it does|
|-|-|-|
|Back end|Python, FastAPI, Uvicorn, Pydantic|Serves the page, assembles prompts, calls the model, checks replies|
|Front end|HTML, CSS, JavaScript (no build step)|The interface and its state (versions, log)|
|AI model|Google Gemini `gemini-3.6-flash` via `google-genai`|Writes answers, revisions and Auto-fix proposals|
|Checks and diffs|Python (`difflib`, rules in `app/checks.py`)|Suggested fixes and change reports, without AI|
|Tests|pytest; Playwright for storyboard capture|Mock-mode tests; scripted browser runs|
|Fonts|Atkinson Hyperlegible, Source Serif 4 (Google Fonts)|Legible interface; reading text|

Undecided: the model is set in `.env` (`GEMINI\\\\\\\\\\\\\\\_MODEL`) and can be changed if
Google renames or retires it; no other model has been tested.

## Running or inspecting the work

Requires Python 3.10 or later and Git.

```bash
git clone https://github.com/meghasannu/fixit-recovery-assistant.git
cd fixit-recovery-assistant
python -m venv .venv
# Windows: .venv\\\\\\\\\\\\\\\\Scripts\\\\\\\\\\\\\\\\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
uvicorn app.main:app --reload
```

Open http://localhost:8000 and choose a demo case. To repeat a storyboard,
pick its demo case (Too technical, or Missing point) and follow its frames in
order.

* **No key needed to inspect it:** leave `GEMINI\\\\\\\\\\\\\\\_API\\\\\\\\\\\\\\\_KEY` empty and the app runs
in mock mode.
* **Live model with your own key:** create a free key in Google AI Studio and
add `GEMINI\\\\\\\\\\\\\\\_API\\\\\\\\\\\\\\\_KEY=...` to `.env`. No key is included in this repository;
never commit `.env`.

```bash
pytest                                   # 52 tests, mock mode
python -m scripts.prompt\\\\\\\\\\\\\\\_tests           # live prompt tests (needs a key)
pip install playwright
python -m scripts.capture\\\\\\\\\\\\\\\_storyboards    # storyboard frames (app running)
```

## Development record

Full notes, with what was checked at each step: `docs/development-notes.md`.
Prompt versions and live test runs: `docs/prompt-log.md` and
`docs/prompt-tests/`. Significant changes, by stage:

1. **Skeleton.** Back end, mock mode, prompts written as specifications with
the pasted text marked as information. Change: the working message moved
onto the clicked button after a browser check showed it off-screen.
2. **Recovery tools.** Buttons with hints, own words, highlighting, history,
undo. Change: only new words highlighted by default after full
strike-through made rewrites unreadable.
3. **Auto-fix.** Proposal first, run only after approval; JSON reply checked
in code. Change: suggestion shown once instead of twice.
4. **Suggested fix and decline.** Change: criteria tightened after false
alarms on good answers (now 3 of 3 failures flagged, 0 of 6 good answers);
a new-words warning was dropped.
5. **Live model.** Seeded demo failures kept in live mode. First live test run
11 of 13: two cases got no answer (service overloaded). Change: retry and
clear errors; rerun 13 of 13.
6. **Interface and session log.** Step path, limits panel, shortcuts,
accessibility, final-answer summary and log. Change: fixed elements shown
before any answer existed; storyboard 2 now ends on the summary.

Commit history: https://github.com/meghasannu/fixit-recovery-assistant/commits/main.
Submitted version: tag `v1.0`
(https://github.com/meghasannu/fixit-recovery-assistant/tree/v1.0).

## AI assistance

I used **Claude (Anthropic)** throughout, and **Google Gemini** is the model
inside the app.

* **Code:** I asked Claude to build each stage from my Assignment 1 design. I
ran the app and the tests after every stage, and used screenshots to check
the interface. Several of its first versions changed after checking (see the
development record), for example the suggestion checks, which raised false
alarms until their criteria were tightened.
* **Prompts:** Claude drafted the prompt specifications; I ran the live prompt
tests on Gemini, and the overloaded-service failures led to the retry change.
* **Report and figures:** Claude drafted the report text, system diagram and
storyboards from the lecture notes, my Assignment 1 and the running app. I
checked every claim against the prototype and every reference against its
source, and edited the text.

## Additional files

None. Everything is in this repository:

* `docs/system-diagram.png`: Figure 1 of the report.
* `docs/storyboards/storyboard-1.png` to `storyboard-3.png`: Figures 2 to 4.
The screens in them were captured in mock mode with
`scripts/capture\\\\\\\\\\\\\\\_storyboards.py`; `docs/storyboards/frames/` holds the
individual frames.
* `docs/prompt-tests/`: reports from the live prompt test runs.

## Project layout

```
app/        Back end: config, prompts, model clients, checks, diffs, mock data
static/     Web page: index.html, style.css, app.js
tests/      Automated tests (mock mode)
scripts/    Live prompt tests; storyboard capture
docs/       Development notes, prompt log, test reports, figures
```

