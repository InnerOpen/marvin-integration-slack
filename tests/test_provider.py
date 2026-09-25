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


def test_check_accepts_bare_token_full_url_and_apprise_form():
    p = SlackProvider()
    assert p.check(_ctx(secret="T00000000/B00000000/xxxxxxxx")) == ("ok", None)  # bare token
    assert p.check(_ctx(secret="https://hooks.slack.com/services/T/B/x")) == ("ok", None)  # full URL
    assert p.check(_ctx(secret="slack://T/B/x")) == ("ok", None)  # apprise-style
    assert p.check(_ctx(secret=None))[0] == "unconfigured"
    assert p.check(_ctx(secret="onepart"))[0] == "error"  # not enough token segments
    assert p.check(_ctx(secret="https://evil.example/webhook"))[0] == "error"  # non-slack URL


def test_send_message_posts_to_normalized_url():
    http = _StubHttp()
    p = SlackProvider()
    result = p.run_action("send_message", {"text": "Recipe published!"}, _ctx(secret="T1/B2/c3", http=http))
    assert result["status_code"] == 200
    assert http.last["url"] == "https://hooks.slack.com/services/T1/B2/c3"  # base prepended
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


def test_provider_declares_the_connection_that_makes_it_useful():
    """A webhook posts nothing until something decides when to send. The provider declares that
    connection so a workspace does not have to wire the same thing by hand."""
    content = SlackProvider().content
    assert [c.kind for c in content] == ["event_subscription"]
    sub = content[0]
    assert sub.payload["event_type"] == "entry_published"
    assert sub.payload["action"] == "send_message"
    # the action it names must be one this provider actually has
    assert sub.payload["action"] in {a.key for a in SlackProvider().actions}
