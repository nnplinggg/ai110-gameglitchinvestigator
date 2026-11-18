"""End-to-end regression tests that drive the real Streamlit app."""
from streamlit.testing.v1 import AppTest


def _guess(at, value):
    at.text_input[0].set_value(str(value))
    at.button[0].click().run()
    return [w.value for w in at.warning]


def _new_app(secret):
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.session_state.secret = secret
    return at


def test_hint_direction_is_consistent_across_attempts():
    # Bug 2 only showed up on every other attempt, so guess several times.
    at = _new_app(50)
    for value in (9, 9, 9, 9):  # always below 50
        assert _guess(at, value) == ["Go HIGHER!"]


def test_high_guess_says_go_lower_on_every_attempt():
    at = _new_app(50)
    for value in (100, 100, 100):  # always above 50
        assert _guess(at, value) == ["Go LOWER!"]


# --- Bug 3 and 5: attempts counter, New Game, difficulty ---
def _info(at):
    return [i.value for i in at.info]


def test_fresh_game_shows_full_attempt_allowance():
    at = _new_app(50)
    assert "Attempts left: 8" in _info(at)[0]


def test_losing_takes_exactly_attempt_limit_guesses():
    at = _new_app(50)
    for _ in range(7):
        _guess(at, 1)
        assert at.session_state.status == "playing"
    _guess(at, 1)  # 8th guess on Normal
    assert at.session_state.status == "lost"


def test_new_game_fully_resets_after_loss():
    at = _new_app(50)
    for _ in range(8):
        _guess(at, 1)
    at.button[1].click().run()
    assert at.session_state.status == "playing"
    assert at.session_state.attempts == 0
    assert at.session_state.score == 0
    assert at.session_state.history == []


def test_new_game_secret_respects_difficulty_range():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.sidebar.selectbox[0].set_value("Easy").run()
    for _ in range(15):
        at.button[1].click().run()
        assert 1 <= at.session_state.secret <= 20


def test_banner_and_secret_follow_difficulty():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.sidebar.selectbox[0].set_value("Easy").run()
    assert "between 1 and 20" in _info(at)[0]
    assert 1 <= at.session_state.secret <= 20


def test_banner_updates_immediately_after_a_guess():
    at = _new_app(50)
    _guess(at, 1)
    assert "Attempts left: 7" in _info(at)[0]
