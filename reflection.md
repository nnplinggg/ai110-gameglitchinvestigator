# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

**First impression.** The game loads fine in Streamlit, but it is unwinnable by reasoning: the hints point the wrong way, and the secret seems to behave differently on every other click. I reproduced everything below by driving the real `app.py` with Streamlit's `AppTest` harness (fixed secret = 50), so each row is a repeatable trigger and not a one-off impression. I did not fix anything in this phase.

**Bugs found**

1. **Inverted hints** (`check_guess`, app.py): a guess above the secret returns "Too High" but the message says "Go HIGHER!"; a guess below returns "Go LOWER!". Following the hint always moves you away from the answer.
2. **Secret turns into a string on even attempts** (submit block, app.py: `if st.session_state.attempts % 2 == 0: secret = str(...)`). `check_guess` then compares `int` to `str`, hits the `TypeError` fallback and compares as strings, so `"9" > "50"` is True and 9 is reported as "Too High".
3. **Off-by-one attempts counter**: `attempts` starts at 1, so the banner says "Attempts left: 7" on Normal (limit 8) before any guess, and the game ends after only 7 real guesses. "New Game" resets it to 0, so the two paths disagree.
4. **Scoring is erratic** (`update_score`): "Too High" gives +5 on even attempts and -5 on odd ones, so wrong guesses can raise your score. A win awards `100 - 10*(attempt+1)`, which double-counts the off-by-one in bug 3.
5. **New Game / difficulty are half-implemented**: "New Game" does not reset `status`, `score` or `history` (after a loss the game stays in "lost" and the next click shows "Game over" again) and always draws the secret from 1 to 100. The banner is hard-coded to "between 1 and 100" even on Easy (1 to 20), and switching difficulty does not redraw the secret.

**Bug Reproduction Log**

| Input | Expected Behavior | Actual Behavior | Console Output / Error | Suspected Code Location |
|-------|-------------------|-----------------|------------------------|-------------------------|
| Secret 50, guess 60 (attempt 1) | "Too High" hint telling me to go **lower** | Message "Go HIGHER!" | none | `check_guess`, app.py (messages swapped) |
| Secret 50, guess 9 on an even attempt (e.g. second guess) | "Too Low" (9 < 50) | Treated as "Too High" because `"9" > "50"` as strings | none (silent `TypeError` caught inside `check_guess`) | submit block `str(secret)` + `check_guess` `except TypeError`, app.py |
| Fresh Normal game, before guessing | "Attempts left: 8" | "Attempts left: 7"; game ends after 7 guesses | none | `st.session_state.attempts = 1` init, app.py |
| Secret 50, guess 60 three times | Score never rises for a wrong guess | Score goes 5, 0, 5 | none | `update_score`, `attempt_number % 2` branch |
| Lose a game, then click "New Game" | Fresh game: score 0, empty history, playing | status still "lost", score -35, history kept, next guess shows "Game over" | none | `if new_game:` block, app.py |
| Switch to Easy (range 1 to 20) | Banner says "between 1 and 20", secret in 1 to 20 | Banner says "1 and 100"; secret was 85 | none | `st.info(...)` text and `secret` init, app.py |

**Asking the AI (human in the loop).** I asked Claude to explain the `check_guess` `try/except TypeError` block step by step. It correctly traced that the `except` branch only exists because `app.py` passes a string secret on even attempts, i.e. the "defensive" code hides bug 2 instead of handling a real case. I did not take that on trust: the AppTest run above (guess 9 vs secret 50 flips between "Go HIGHER!" and "Go LOWER!" on alternating attempts) matches exactly what that explanation predicts.

---

## 2. How did you use AI as a teammate?

**Tools.** Claude Code (Claude Sonnet 5.5) running in VS Code, used as an agent that could read the repo, run pytest and the app, and edit files. I set the plan (log first, fix two bugs, then the rest, three or more commits) and reviewed every diff before committing.

**Correct suggestion.** When I asked for an explanation of `check_guess`, Claude pointed out that the `except TypeError` string-comparison fallback was not real defensive code: it only existed because `app.py` passed `str(secret)` on even attempts. Its fix was to delete the fallback and the `str()` call so the secret is always an int, rather than patching the comparison. It was right because the bug disappeared at its source. I verified it by running the same two app-level tests (`tests/test_app_flow.py`) against the original `app.py`, where they failed, and against the fixed one, where they pass.

**Suggestion I did not accept as written.** The three starter tests failed with `NotImplementedError`, and the fastest way to get them green was to make `check_guess` return a bare string like `"Win"`, which is what the tests compare against. I rejected that: the function's docstring and `app.py` both rely on `(outcome, message)`, and the message is exactly where bug 1 lived. I kept the tuple and changed the three starter tests to unpack it, adding two tests that assert the message direction. I confirmed the new message tests failed on the swapped messages before I fixed them.

---

## 3. Debugging and testing your fixes

I counted a bug as fixed only when (a) a test that failed on the original code now passes and (b) the same scenario behaves correctly in the real app. The core pattern was red, green: write the test, watch it fail for the right reason, then change the code. For bug 1 the two message tests failed with swapped text; for bug 2 the `check_guess` unit tests passed on the moved-but-unfixed code, which taught me the bug was in `app.py` and not in the function, so I wrote Streamlit `AppTest` tests that click through several attempts.

Evidence: `pytest -v` gives 20 passed (saved in `test_results.txt`), and `python -m streamlit run app.py` started cleanly (health endpoint returned 200). A scripted game with secret 50 returned "Go HIGHER!" for 40, "Go LOWER!" for 70 and 60, and a win on the fourth guess with score 45. Claude drafted most of the test cases, but I chose the edge cases that matter here (every other attempt, floor of 10 points, reset after a loss). One of its first assertions failed because Streamlit strips the emoji from the message text, which was a test bug and not a code bug.

---

## 4. What did you learn about Streamlit and state?

Streamlit re-runs the whole script from top to bottom every time you click or type anything, so ordinary variables are rebuilt each time. `st.session_state` is a dictionary that survives those reruns, which is where the secret number, attempts and score must live. Two bugs here came from that model: the banner was drawn before the submit code updated the attempts, so it lagged one guess behind, and "New Game" only reset some of the stored values. Initialising state in one `reset_game()` and redrawing the banner after the guess fixed both.

---

## 5. Looking ahead: your developer habits

- **Habit to reuse:** write the failing test first and make sure it fails for the reason I expect. It showed me that bug 2 was not where I first assumed, which a "fix then test" order would have hidden.
- **Do differently:** I would ask the AI for a short plan and the list of files it intends to touch before it edits anything, and I would check every claim it writes into the docs. My first draft of this log said I had confirmed something by logging types when I had actually used the AppTest run, so I corrected it before pushing.
- **How my view changed:** AI-generated code can look tidy and still carry silent logic errors (swapped messages, a fallback that hides a bug), so it needs the same tests and review as any code. The AI is a fast pair programmer, but the verification and the decisions are still mine.
