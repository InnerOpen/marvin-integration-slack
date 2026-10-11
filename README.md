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

1. In Slack, create an **Incoming Webhook** for the target channel.
2. In Marvin: **Settings → Integrations → Slack → Configure**, paste the **webhook token** — the
   `T00000000/B00000000/XXXX` path (the same value Apprise uses as `slack://<token>`). A full
   `https://hooks.slack.com/services/...` URL works too. Save.
3. Use the **Send message** action from an automation, or test-fire it from the integration card.

The provider knows the `hooks.slack.com/services/` base URL, so you only supply the token.

## Credential & action

| | |
|---|---|
| **Credential** | `webhook_token` — the webhook token path (`T…/B…/…`), or a full webhook URL |
| **Action** | `send_message` — `{ "text": "..." }`, or `{ "title": "...", "body": "..." }` (title in bold over the body). It is the standard **`notify`** capability, so a workflow or Workflow Library recipe that sends a notification can use Slack as well as Apprise. |

## What it teaches Marvin (0.4.0, SDK 0.9.0)

- **A guide** (`src/marvin_integration_slack/guide.md`): connecting a webhook, formatting, what it can't do, and
  what each Slack error means. Marvin's agents read it when building workflows where Slack is connected, and
  Marvin's manual search finds it.
- **A recipe** in the Workflow Library, *Announce published entries*: each published entry of one type is posted to
  the channel with its title and link. Shown as "From the Slack plugin 0.4.0", offered once Slack is connected.

## Develop

```bash
uv run --extra dev pytest
```

The provider depends only on `marvin-integration-sdk` — not on Marvin core — so tests run standalone.
