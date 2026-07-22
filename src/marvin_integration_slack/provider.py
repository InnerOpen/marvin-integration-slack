"""Slack provider — post messages to a channel via an incoming webhook."""

from marvin_integration_sdk import (
    CATEGORY_NOTIFY,
    CredentialField,
    IntegrationContext,
    IntegrationProvider,
    ProviderAction,
    register_provider,
)

_WEBHOOK_PREFIX = "https://hooks.slack.com/"


@register_provider
class SlackProvider(IntegrationProvider):
    slug = "slack"
    name = "Slack"
    description = "Post messages to a Slack channel via an incoming webhook."
    category = CATEGORY_NOTIFY

    credentials = (
        CredentialField(
            key="webhook_url",
            label="Incoming Webhook URL",
            help="Slack → your app → Incoming Webhooks. The URL contains a secret token, so it is stored as a secret.",
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
            return ("unconfigured", "Missing webhook URL.")
        if not ctx.secret.startswith(_WEBHOOK_PREFIX):
            return ("error", "That doesn't look like a Slack incoming webhook URL.")
        return ("ok", None)

    def run_action(self, key: str, args: dict, ctx: IntegrationContext) -> dict:
        if key != "send_message":
            raise NotImplementedError(f"slack has no action '{key}'")
        if not ctx.secret:
            raise ValueError("No webhook URL configured.")
        text = (args or {}).get("text")
        if not text:
            raise ValueError("A 'text' message is required.")

        try:
            resp = ctx.http.post(ctx.secret, json={"text": text})
        except Exception as e:  # noqa: BLE001 — surface transport/guard failures cleanly
            ctx.logger.warning(f"[slack] webhook unreachable: {e}")
            raise ValueError(f"Slack webhook unreachable: {e}") from e

        if not resp.ok:
            raise ValueError(f"Slack returned HTTP {resp.status_code}: {resp.text[:200]}")
        return {"status_code": resp.status_code}
