# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

**Purpose.** A Streamlit number-guessing game: pick a difficulty, guess the secret number within a limited number of attempts, get "Go HIGHER" or "Go LOWER" hints, and earn a score. The starter was AI-generated and deliberately broken; my job was to find, explain and repair the bugs with tests.

**Bugs found** (full reproduction table in `reflection.md`):
1. Hints were inverted (`check_guess`).
2. The secret was converted to a string on even attempts, causing string comparison (`app.py`).
3. Attempts started at 1, so the counter and loss point were off by one.
4. Scoring was erratic (wrong guesses could add points).
5. "New Game" did not reset state; the banner and secret ignored the difficulty range.
6. The attempts banner lagged one guess behind (found while writing the demo).

**Fixes applied.** Game logic now lives in `logic_utils.py` (`get_range_for_difficulty`, `parse_guess`, `check_guess`, `update_score`) and `app.py` only does the UI. `check_guess` compares ints and returns correct hints, `update_score` is deterministic, and a single `reset_game()` handles first load, New Game and difficulty changes. Every fix has a regression test, and each bug is marked with a `FIXME` that was replaced by a `FIX` comment describing how the AI and I split the work.

## 📸 Demo Walkthrough

A sample game on Normal difficulty (1 to 100, 8 attempts) with the secret set to 50:

1. The banner reads "Guess a number between 1 and 100. Attempts left: 8".
2. I guess 40: the game says "Go HIGHER!", the score is -5 and the banner immediately shows "Attempts left: 7".
3. I guess 70: "Go LOWER!", score -10, attempts left 6.
4. I guess 60: "Go LOWER!", score -15.
5. I guess 50: "Correct!", balloons, and "You won! The secret was 50. Final score: 45".
6. Further guesses show "You already won. Start a new game to play again."
7. Clicking "New Game" resets the score to 0, clears the history, and draws a new secret within the selected range.

## 🧪 Test Results

`pytest -v` (also saved in `test_results.txt`):

```
============================= test session starts ==============================
platform darwin -- Python 3.14.6, pytest-9.2.0, pluggy-1.7.0 -- /Users/xps/ai110-gameglitchinvestigator/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/xps/ai110-gameglitchinvestigator
plugins: anyio-4.16.0
collecting ... collected 20 items

tests/test_app_flow.py::test_hint_direction_is_consistent_across_attempts PASSED [  5%]
tests/test_app_flow.py::test_high_guess_says_go_lower_on_every_attempt PASSED [ 10%]
tests/test_app_flow.py::test_fresh_game_shows_full_attempt_allowance PASSED [ 15%]
tests/test_app_flow.py::test_losing_takes_exactly_attempt_limit_guesses PASSED [ 20%]
tests/test_app_flow.py::test_new_game_fully_resets_after_loss PASSED     [ 25%]
tests/test_app_flow.py::test_new_game_secret_respects_difficulty_range PASSED [ 30%]
tests/test_app_flow.py::test_banner_and_secret_follow_difficulty PASSED  [ 35%]
tests/test_app_flow.py::test_banner_updates_immediately_after_a_guess PASSED [ 40%]
tests/test_game_logic.py::test_winning_guess PASSED                      [ 45%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [ 50%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 55%]
tests/test_game_logic.py::test_too_high_message_tells_player_to_go_lower PASSED [ 60%]
tests/test_game_logic.py::test_too_low_message_tells_player_to_go_higher PASSED [ 65%]
tests/test_game_logic.py::test_numeric_not_lexicographic_comparison_low PASSED [ 70%]
tests/test_game_logic.py::test_numeric_not_lexicographic_comparison_high PASSED [ 75%]
tests/test_game_logic.py::test_wrong_guess_never_raises_score PASSED     [ 80%]
tests/test_game_logic.py::test_first_attempt_win_scores_90 PASSED        [ 85%]
tests/test_game_logic.py::test_win_score_has_floor_of_10 PASSED          [ 90%]
tests/test_game_logic.py::test_difficulty_ranges PASSED                  [ 95%]
tests/test_game_logic.py::test_parse_guess_edge_cases PASSED             [100%]

============================== 20 passed in 0.97s ==============================
```

## 🚀 Stretch Features

- Not attempted.
