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
