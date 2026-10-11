# Slack

Posts messages to **one Slack channel** through a Slack incoming webhook. One connection is one channel: to post to
another channel, connect Slack again with that channel's webhook.

## Connect it

1. In Slack, open **api.slack.com/apps → Create New App → From scratch**, pick your Slack workspace.
2. **Incoming Webhooks** → switch on → **Add New Webhook to Workspace** → choose the channel → copy the webhook URL.
3. In Marvin: **Settings → Integrations → Slack → Connect**, paste the URL (or just its `T…/B…/…` token part) as the
   **Webhook Token**, save, and send a test from the integration card.

## Send a message

The action is **Send message** (`send_message`):

- `text` — the message, or
- `title` + `body` — the title in bold above the body.

It is Marvin's **notify** capability, so notification recipes and alerts can send through Slack as well as Apprise.
In a workflow, `${entry.title}`, `${entry.url}` and other templates are filled in when it runs.

Slack formatting works in the text: `*bold*`, `_italic_`, `<https://example.com|link text>`, and line breaks. Links
to pages usually unfurl into a preview.

The **Announce published entries** recipe in the Workflow Library posts each published entry of one type, with its
link — a good first workflow.

## What it can't do

- Read messages, reply in threads, react, or send direct messages — a webhook only posts.
- Upload files or images (post a link instead).
- Change the channel — a webhook is tied to the channel chosen when it was made.

## When it fails

- **`no_service`** or **`invalid_token`** (404 / 403) — the webhook was removed or the Slack app uninstalled: make a new one.
- **404 `channel_not_found`** / **410 `channel_is_archived`** — the channel is gone or archived.
- **403 `action_prohibited`** — a Slack admin restricted posting to that channel.
- Slack accepts about **one message per second** per webhook; a burst (a bulk publish) may be rate limited.
