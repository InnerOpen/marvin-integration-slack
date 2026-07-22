"""Tests for the Slack provider — check logic + send_message, with a stub http helper."""

import logging

import pytest

from marvin_integration_sdk import IntegrationContext
from marvin_integration_slack import SlackProvider

_LOG = logging.getLogger("test")


class _StubHttp:
    """Records the last POST and returns a canned response."""

    def __init__(self, status=200):
        self.status = status
        self.last = None

    def get(self, url, *, headers=None, timeout=15):  # pragma: no cover - unused
        raise AssertionError("no GET expected")

    def post(self, url, *, json=None, data=None, headers=None, timeout=15):
        from marvin_integration_sdk import Response

        self.last = {"url": url, "json": json}
        return Response(status_code=self.status, content=b"ok")


def _ctx(secret=None, http=None):
    return IntegrationContext(config={}, secret=secret, logger=_LOG, http=http or _StubHttp())


def test_check_logic():
    p = SlackProvider()
    assert p.check(_ctx(secret="https://hooks.slack.com/services/T/B/x")) == ("ok", None)
    assert p.check(_ctx(secret=None))[0] == "unconfigured"
    assert p.check(_ctx(secret="https://evil.example/webhook"))[0] == "error"


def test_send_message_posts_text():
    http = _StubHttp()
    p = SlackProvider()
    result = p.run_action("send_message", {"text": "Recipe published!"}, _ctx(secret="https://hooks.slack.com/x", http=http))
    assert result["status_code"] == 200
    assert http.last["json"] == {"text": "Recipe published!"}


def test_send_message_requires_text():
    p = SlackProvider()
    with pytest.raises(ValueError):
        p.run_action("send_message", {}, _ctx(secret="https://hooks.slack.com/x"))


def test_unknown_action_raises():
    p = SlackProvider()
    with pytest.raises(NotImplementedError):
        p.run_action("nope", {}, _ctx(secret="https://hooks.slack.com/x"))


def test_send_message_surfaces_http_error():
    p = SlackProvider()
    with pytest.raises(ValueError):
        p.run_action("send_message", {"text": "hi"}, _ctx(secret="https://hooks.slack.com/x", http=_StubHttp(status=404)))
