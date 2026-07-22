"""Slack provider — post messages to a channel via an incoming webhook.

The provider knows the webhook base URL, so the credential is just the *token* — the
``T00000000/B00000000/XXXX`` path, the same value Apprise uses as ``slack://<token>``.
A full ``https://hooks.slack.com/services/...`` URL is accepted too.
"""

from marvin_integration_sdk import (
    CATEGORY_NOTIFY,
    CredentialField,
    IntegrationContext,
    IntegrationProvider,
    ProviderAction,
    register_provider,
)

_BASE = "https://hooks.slack.com/services/"


def _webhook_url(secret: str) -> str:
    """Normalize whatever the user pasted into a full webhook URL.

    Accepts the bare token (``T.../B.../C``), an Apprise-style ``slack://T.../B.../C``,
    or the full ``https://hooks.slack.com/...`` URL.
    """
    s = secret.strip()
    if s.startswith("slack://"):
        s = s[len("slack://") :]
    if s.startswith(("http://", "https://")):
        return s
    return _BASE + s.lstrip("/")


def _looks_like_webhook(url: str) -> bool:
    if not url.startswith("https://hooks.slack.com/services/"):
        return False
    tail = url.split("hooks.slack.com/services/", 1)[-1]
    return len([part for part in tail.split("/") if part]) >= 3


@register_provider
class SlackProvider(IntegrationProvider):
    slug = "slack"
    name = "Slack"
    description = "Post messages to a Slack channel via an incoming webhook."
    category = CATEGORY_NOTIFY

    credentials = (
        CredentialField(
            key="webhook_token",
            label="Webhook Token",
            help="The token part of a Slack incoming webhook — T00000000/B00000000/XXXX "
            "(the same value Apprise uses as slack://<token>). A full https://hooks.slack.com/… URL also works.",
        ),
    )
    actions = (
        ProviderAction(
            key="send_message",
            label="Send message",
            description="Post a message to the channel wired to this webhook.",
            input_schema={
                "type": "object",
                "properties": {"text": {"type": "string", "title": "Message"}},
                "required": ["text"],
                "additionalProperties": False,
            },
        ),
    )

    def check(self, ctx: IntegrationContext) -> tuple[str, str | None]:
        if not ctx.secret:
            return ("unconfigured", "Missing webhook token.")
        if not _looks_like_webhook(_webhook_url(ctx.secret)):
            return ("error", "Expected a Slack webhook token like T00000000/B00000000/XXXXXXXX (or the full URL).")
        return ("ok", None)

    def run_action(self, key: str, args: dict, ctx: IntegrationContext) -> dict:
        if key != "send_message":
            raise NotImplementedError(f"slack has no action '{key}'")
        if not ctx.secret:
            raise ValueError("No webhook token configured.")
        text = (args or {}).get("text")
        if not text:
            raise ValueError("A 'text' message is required.")

        try:
            resp = ctx.http.post(_webhook_url(ctx.secret), json={"text": text})
        except Exception as e:  # noqa: BLE001 — surface transport/guard failures cleanly
            ctx.logger.warning(f"[slack] webhook unreachable: {e}")
            raise ValueError(f"Slack webhook unreachable: {e}") from e

        if not resp.ok:
            raise ValueError(f"Slack returned HTTP {resp.status_code}: {resp.text[:200]}")
        return {"status_code": resp.status_code}
