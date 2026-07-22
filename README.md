# marvin-integration-slack

A [Marvin](https://claude.ai/code) integration that posts messages to a Slack channel via an
**incoming webhook**. Category: *notify*.

Wire it to an automation — e.g. *on entry published → Slack: send message "New recipe: {{title}}"* —
to announce content to your team or community when you publish.

## Install

On a Marvin host:

```bash
uv pip install marvin-integration-slack   # or add to your Marvin image
# restart Marvin → "Slack" appears in Settings → Integrations
```

That's it — no changes to Marvin core or its frontend. Marvin discovers the provider through the
`marvin.integrations` entry point this package declares.

## Configure

1. In Slack, create an **Incoming Webhook** for the target channel; copy the webhook URL.
2. In Marvin: **Settings → Integrations → Slack → Configure**, paste the webhook URL (stored as a
   secret), and save.
3. Use the **Send message** action from an automation, or test-fire it from the integration card.

## Credential & action

| | |
|---|---|
| **Credential** | `webhook_url` — the Slack incoming webhook (contains a secret token) |
| **Action** | `send_message` — `{ "text": "..." }` |

## Develop

```bash
uv run --extra dev pytest
```

The provider depends only on `marvin-integration-sdk` — not on Marvin core — so tests run standalone.
