# Clients in Zulip

`zerver.models.Client` is Zulip's analogue of the HTTP User-Agent
header (and is populated from User-Agent). It exists for use in
analytics and other places to provide human-readable summary data
about "which Zulip client" was used for an operation (e.g., was it the
Android app, the desktop app, or a bot?).

In general, it shouldn't be used for anything controlling the behavior
of Zulip; it's primarily intended to assist debugging.

## Analytics

A `Client` is used to sort messages into client categories such as
`ZulipElectron` on the `/stats` page. For more information see,
[Analytics](analytics.md).

## Integrations

Generally, integrations in Zulip should declare a unique User-Agent,
so that it's easy to figure out which integration is involved when
debugging an issue. For incoming webhook integrations, we do that
conveniently via the auth decorators (as we will describe shortly);
other integrations generally should set the first User-Agent element
on their HTTP requests to something of the form
ZulipIntegrationName/1.2 so that they are categorized properly.

The `webhook_view` auth decorator, used for most incoming
webhooks, accepts the name of the integration as an argument and uses
it to generate a client name that it adds to the `request_notes`
object that can be accessed with the `request` (Django
[HttpRequest](https://docs.djangoproject.com/en/5.0/ref/request-response/#django.http.HttpRequest))
object via `zerver.lib.request.get_request_notes(request)`.

In most integrations, `request_notes.client` is then passed to
`check_send_webhook_message`, where it is used to keep track of which client
sent the message (which in turn is used by analytics). For more
information, see [the incoming webhook walkthrough](https://zulip.com/api/incoming-webhooks-walkthrough).
