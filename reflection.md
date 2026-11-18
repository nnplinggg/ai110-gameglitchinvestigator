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

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
