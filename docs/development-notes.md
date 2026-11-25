# Development notes

Working notes for the README development record. Each entry: what changed, why,
and how it was checked.

## Stage 1: project skeleton

- **Built:** FastAPI backend; Gemini client and mock client behind one
  interface; prompt specifications (`app/prompts.py`); input/output page;
  "show what was sent" panel; three seeded demo failures; 8 tests.
- **Change during build: working feedback moved onto the Generate button.**
  In a browser check, clicking Generate low on the page left the "Working on
  it" message off-screen at the top of the answer panel, so the click seemed to
  do nothing. The message now also appears on the button, where attention
  already is (inattentional blindness and feedback timing, Lecture 04).
  Checked with a scripted browser run and screenshots.
- **Change during build: simulated delay in mock mode** (800 ms, configurable)
  so the waiting feedback behaves as it would with the live model.
- **Change during build: demo label clears when the text is edited**, so the
  interface never claims an edited text is still a demo case.

## Stage 2: recovery tools

- **Built:** five correction buttons with a hint box (hover or keyboard focus);
  free-text correction; `/api/revise`; word-level change detection and report
  computed by code (`app/diffing.py`); version history with authorship labels
  ("You chose this fix; the AI rewrote the answer"); Undo; 9 new tests.
- **Design decision: hints come from the prompt specification.** Each button's
  hint is served from the same `REVISIONS` entry as its prompt, so the preview
  cannot drift from what the button really asks for (feedforward, gulf of
  execution, L06).
- **Design decision: a hint box, not browser tooltips.** Native tooltips appear
  after a delay and not on keyboard focus; a fixed hint box is visible, readable
  and works with the keyboard.
- **Change during build: highlighting new words only by default.** The first
  version showed added and removed words inline. In a browser check of the
  "Simpler" rewrite, nearly every word was struck through or highlighted and the
  answer became hard to read (extraneous cognitive load, L05). The default now
  highlights only new words; removed words are an option. A "Mostly rewritten"
  note is added when 60% or more of the words were removed.
- **Design decision: Undo never deletes.** Undo returns to the version the
  current one was made from; every version stays in the history and can be
  reopened, so an undo can itself be undone (reversibility, L01).
- **Checked:** 17 tests pass; scripted browser walk-through of three scenarios
  (too technical → Simpler; Shorter makes it worse → Undo → own correction;
  missing point → Fix missing point) with screenshots.

## Stage 3: Auto-fix (visible, editable prompt rewrite)

- **Built:** `/api/autofix` returns a proposal only (diagnosis, rewritten
  request, changes, assumptions); nothing is generated until the person clicks
  "Run this request". The request diff is computed by code. The approved
  request replaces the request on screen, and the new version is labelled
  "The AI proposed a new request; you approved it" or "you edited and approved
  it". Cancel changes nothing.
- **Design decision: confirm before running.** Buttons run at once because
  their result is visible and undoable; Auto-fix changes the request, which is
  the person's intent, so it is confirmed first (reversible/visible quadrant,
  L12; Shneiderman's two dimensions: high automation with high control).
- **Design decision: assumptions shown separately and highlighted.** Guesses
  about the person are the part most likely to be wrong and most likely to be
  accepted without reading (anchoring, automation bias, L06).
- **Design decision: validate the JSON in code.** Malformed or incomplete
  proposals are caught and reported ("Nothing was changed"), never shown as
  valid (schema guarantees shape, not truth, L09).
- **Change during build: the suggestion is shown once.** The first version
  showed the highlighted suggestion and an edit box with the same text, so the
  person read it twice. The edit box now opens only via "Edit the suggestion"
  (extraneous load, L05). Checked with screenshots.
- **Checked:** 27 tests pass; scripted browser run of propose → edit → run,
  and propose → cancel.

## Stage 4: suggested fix and decline

- **Built:** `app/checks.py` runs three checks in code on every answer and
  returns findings with the button they suggest; a "FixIt noticed (you decide
  whether to act)" panel; the suggested button is highlighted; each finding can
  be dismissed ("Not a problem"); mock mode demonstrates the decline turn.
  17 new tests (44 in total).
- **Design decision: suggest, never apply.** The system infers a likely problem
  but the person decides (mixed initiative, ask rather than act, L03). This
  also gives the system a signal beyond explicit commands, the first of the
  four properties in the module's working definition (L02).
- **Design decision: checks in code, not a second model call.** They are fast,
  free, repeatable, and their evidence can be shown ("178 words; you asked for
  about 60").
- **Change during build: criteria tightened after false alarms.** The first
  version fired on good answers: a plain-language rewrite was flagged as
  jargon because of ordinary new words ("sunlight", "brighter"), and a request
  saying "leave out examples" produced a "missing point" about the example.
  Following the cry-wolf effect (L04), the criteria were made cautious: the
  jargon check needs at least 4 such words making up 10% of the answer; the
  missing-point check ignores what the request says to leave out and only
  flags gaps that are at least 20% of the source's content. Result on the demo
  set: 3 of 3 bad answers flagged, 0 of 6 good answers flagged (tested).
- **Idea rejected: warning about new words after every revision.** It flagged
  ordinary paraphrase words on good rewrites; the false-alarm cost was too
  high for the value, so the decline behaviour stays in the prompt instead.

## Stage 5: live model and prompt testing

- **Change: seeded demo failures in live mode too.** A real model usually
  writes a good first answer, so the three demo failures would not appear live
  and recovery could not be demonstrated. An unchanged demo case now always
  starts from its scripted bad answer, labelled "Seeded demo failure, not
  written by the model"; all later steps use the live model. This follows the
  seeded unsatisfactory summaries in the Assignment 1 study design.
- **Built:** `scripts/prompt_tests.py`, a fixed testing loop (L09): 8 cases,
  13 criteria checkable by code (default and requested length, ignoring an
  instruction hidden in the source, each fix meeting its success criterion,
  declining an unsupported request, a valid Auto-fix proposal). Results are
  saved to `docs/prompt-tests/` and linked from the prompt log. `--repeat`
  reruns cases to show non-determinism (L08).
- **First live run (2026-11-16, gemini-3.6-flash):** every criterion that ran
  passed (11 of 11), including ignoring an instruction hidden in the source.
  Two cases never got an answer: Google returned "503 UNAVAILABLE, high
  demand".
- **Change from the live run: retry and clearer errors.** A busy service would
  have broken a live demo with a raw error. The client now retries busy and
  rate-limit errors twice (after 2 s and 5 s) and does not retry errors that
  cannot fix themselves (bad key, wrong model name). Messages are now actionable
  ("Google's model is busy right now… Nothing was changed; you can try again").
  The test runner records model errors as "not scored", so a busy server is not
  counted as a failed prompt. 2 new tests (49 in total).

## Stage 6: storyboards

- **Built:** `scripts/capture_storyboards.py` drives the running app through the
  three storyboard scenarios and saves each frame, cropped to the relevant part
  of the page, so the storyboards show real interactions with the live model and
  can be recaptured after any change.
- **Change from drafting the storyboards: the request box is now two lines.**
  An approved Auto-fix request did not fit in the one-line box, so the person
  could not see the request their answer was now based on.
- Frames follow the Lecture 06 method: goal, person's action, system inference
  and action, result and recovery, each marked with who acts, which gulf, and
  which signifier.

## Stage 7: interface refinement and session summary

Constraint for this stage: no change to prompts (still v3, so the 13/13 live
results stay valid) and no change to existing behaviour; all earlier tests
must still pass.

- **Visual redesign (CSS only).** Concept: a reading desk with an editor's pen.
  Answers are set in a serif reading face with a margin rule; new words are
  shown as highlighter strokes; one accent colour (pen blue) marks what to do
  next, amber is reserved for "FixIt noticed", teal for a finished answer.
  Interface font Atkinson Hyperlegible was chosen for low-vision legibility.
  Aim: less extraneous load (L05), a minimalist design (Nielsen).
- **Step path** (paste, get an answer, fix it) that fills in as the person
  goes: visibility of system status, and a system image that supports an
  accurate mental model (L05). The card headings lost their numbers, since the
  step path now carries the sequence.
- **"How FixIt works" panel** listing what it does, what it can't do, and
  shortcuts: make clear what the system can do and how well (Amershi et al.),
  narrowing the expectation gulf (L03).
- **Copy button** and **keyboard shortcuts** (Ctrl+Enter generate; Ctrl+Z
  undo, only outside text boxes so the browser's own text undo still works):
  efficient invocation (Amershi et al.).
- **Accessibility pass:** visible keyboard focus everywhere, skip link,
  `aria-current` on the step path and history, reduced-motion support, text
  contrast checked against WCAG AA.
- **"This answer works for me" and session summary.** Marking a final answer
  shows time to the final answer, fixes by method, Auto-fix runs, undos and
  suggested fixes used, and offers a JSON log download. These are the
  measures of the Assignment 1 study (time, success, recovery attempts), so
  the measurement instrument is now built; running the study with
  participants remains planned. The log holds counts and timings only, never
  the person's text, and stays on the page unless downloaded (store less, L10).
- **Change during build: hidden elements were showing.** The new layout rules
  overrode the `hidden` attribute, so Undo, Copy and the accept button appeared
  before any answer existed. Fixed with a global rule; caught in a screenshot.
- **Change during build: the final-answer button looked disabled.** After
  marking, the greyed-out button read as an error; it now turns solid teal to
  confirm success.
- **Storyboard 2 now ends on the summary** instead of the request box, closing
  the loop that the goal frame opens.
- **Checked:** 51 tests pass (2 new page tests); scripted browser walk-through
  of shortcuts, copy, accept, summary and log download (log contains no text);
  desktop and phone-width screenshots.

## Stage 8: report figures

- **Built:** system diagram (`docs/system-diagram.png`) laid out on the
  module's conceptual spine, with implemented, simulated and planned parts
  marked and the empty layers named; three storyboards
  (`docs/storyboards/`) following the five-frame method, each frame marked
  with who acts, which gulf and which signifier.
- **Change: a scripted mock answer for one own-words correction.** In mock
  mode, storyboard 3's own-words frame showed a placeholder; a scripted answer
  for that demo correction (clearly mock) now shows the interaction properly.
  1 new test (52 in total).
- **README completed** to the brief: status, stack, running, development
  record, AI assistance, additional files and prose word count.
