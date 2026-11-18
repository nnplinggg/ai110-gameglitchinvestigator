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
