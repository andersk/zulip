import importlib
import json
import os
from typing import Any, Callable, Dict

from django.utils.translation import ugettext as _

from zerver.lib.actions import (
    internal_send_huddle_message,
    internal_send_private_message,
    internal_send_stream_message_by_name,
)
from zerver.lib.bot_config import ConfigError, get_bot_config
from zerver.lib.bot_storage import (
    get_bot_storage,
    is_key_in_bot_storage,
    remove_bot_storage,
    set_bot_storage,
)
from zerver.lib.integrations import EMBEDDED_BOTS
from zerver.lib.topic import get_topic_from_message_info
from zerver.models import UserProfile, get_active_user

our_dir = os.path.dirname(os.path.abspath(__file__))

from zulip_bots.lib import RateLimit


def get_bot_handler(service_name: str) -> Any:

    # Check that this service is present in EMBEDDED_BOTS, add exception handling.
    configured_service = ""
    for embedded_bot_service in EMBEDDED_BOTS:
        if service_name == embedded_bot_service.name:
            configured_service = embedded_bot_service.name
    if not configured_service:
        return None
    bot_module_name = f"zulip_bots.bots.{configured_service}.{configured_service}"
    bot_module: Any = importlib.import_module(bot_module_name)
    return bot_module.handler_class()


class StateHandler:
    storage_size_limit: int = 10000000  # TODO: Store this in the server configuration model.

    def __init__(self, user_profile: UserProfile) -> None:
        self.user_profile = user_profile
        self.marshal: Callable[[object], str] = lambda obj: json.dumps(obj)
        self.demarshal: Callable[[str], object] = lambda obj: json.loads(obj)

    def get(self, key: str) -> object:
        return self.demarshal(get_bot_storage(self.user_profile, key))

    def put(self, key: str, value: object) -> None:
        set_bot_storage(self.user_profile, [(key, self.marshal(value))])

    def remove(self, key: str) -> None:
        remove_bot_storage(self.user_profile, [key])

    def contains(self, key: str) -> bool:
        return is_key_in_bot_storage(self.user_profile, key)


class EmbeddedBotQuitException(Exception):
    pass


class EmbeddedBotEmptyRecipientsList(Exception):
    pass


class EmbeddedBotHandler:
    def __init__(self, user_profile: UserProfile) -> None:
        # Only expose a subset of our UserProfile's functionality
        self.user_profile = user_profile
        self._rate_limit = RateLimit(20, 5)
        self.full_name = user_profile.full_name
        self.email = user_profile.email
        self.storage = StateHandler(user_profile)
        self.user_id = user_profile.id

    def send_message(self, message: Dict[str, Any]) -> None:
        if not self._rate_limit.is_legal():
            self._rate_limit.show_error_and_exit()

        if message["type"] == "stream":
            internal_send_stream_message_by_name(
                self.user_profile.realm, self.user_profile, message["to"], message["topic"], message["content"],
            )
            return

        assert message["type"] == "private"
        # Ensure that it's a comma-separated list, even though the
        # usual 'to' field could be either a List[str] or a str.
        recipients = ",".join(message["to"]).split(",")

        if len(message["to"]) == 0:
            raise EmbeddedBotEmptyRecipientsList(_("Message must have recipients!"))
        elif len(message["to"]) == 1:
            recipient_user = get_active_user(recipients[0], self.user_profile.realm)
            internal_send_private_message(
                self.user_profile.realm, self.user_profile, recipient_user, message["content"],
            )
        else:
            internal_send_huddle_message(
                self.user_profile.realm, self.user_profile, recipients, message["content"],
            )

    def send_reply(self, message: Dict[str, Any], response: str) -> None:
        if message["type"] == "private":
            self.send_message(
                dict(
                    type="private",
                    to=[x["email"] for x in message["display_recipient"]],
                    content=response,
                    sender_email=message["sender_email"],
                ),
            )
        else:
            self.send_message(
                dict(
                    type="stream",
                    to=message["display_recipient"],
                    topic=get_topic_from_message_info(message),
                    content=response,
                    sender_email=message["sender_email"],
                ),
            )

    # The bot_name argument exists only to comply with ExternalBotHandler.get_config_info().
    def get_config_info(self, bot_name: str, optional: bool = False) -> Dict[str, str]:
        try:
            return get_bot_config(self.user_profile)
        except ConfigError:
            if optional:
                return dict()
            raise

    def quit(self, message: str = "") -> None:
        raise EmbeddedBotQuitException(message)
