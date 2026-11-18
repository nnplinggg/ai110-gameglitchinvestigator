from logic_utils import check_guess


# check_guess returns (outcome, message). The starter tests compared the whole
# return value to a string, which contradicts the documented contract, so they
# now unpack the tuple and assert on the outcome.
def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Regression: Bug 1, hint message pointed the wrong way ---
def test_too_high_message_tells_player_to_go_lower():
    _, message = check_guess(60, 50)
    assert "LOWER" in message.upper()
    assert "HIGHER" not in message.upper()


def test_too_low_message_tells_player_to_go_higher():
    _, message = check_guess(40, 50)
    assert "HIGHER" in message.upper()
    assert "LOWER" not in message.upper()


# --- Regression: Bug 2, secret was str() on even attempts -> string compare ---
def test_numeric_not_lexicographic_comparison_low():
    # "9" > "50" is True for strings; numerically 9 is Too Low
    assert check_guess(9, 50)[0] == "Too Low"


def test_numeric_not_lexicographic_comparison_high():
    # "100" < "50" is True for strings; numerically 100 is Too High
    assert check_guess(100, 50)[0] == "Too High"


# --- Bug 4: scoring ---
from logic_utils import get_range_for_difficulty, parse_guess, update_score


def test_wrong_guess_never_raises_score():
    for attempt in range(1, 10):  # odd and even attempts
        assert update_score(0, "Too High", attempt) < 0
        assert update_score(0, "Too Low", attempt) < 0


def test_first_attempt_win_scores_90():
    assert update_score(0, "Win", 1) == 90


def test_win_score_has_floor_of_10():
    assert update_score(0, "Win", 50) == 10


# --- Difficulty ranges and input parsing (edge cases) ---
def test_difficulty_ranges():
    assert get_range_for_difficulty("Easy") == (1, 20)
    assert get_range_for_difficulty("Normal") == (1, 100)
    assert get_range_for_difficulty("Hard") == (1, 50)


def test_parse_guess_edge_cases():
    assert parse_guess("") == (False, None, "Enter a guess.")
    assert parse_guess(None) == (False, None, "Enter a guess.")
    assert parse_guess("abc")[0] is False
    assert parse_guess("42") == (True, 42, None)
    assert parse_guess("3.7") == (True, 3, None)
    assert parse_guess("-5") == (True, -5, None)
