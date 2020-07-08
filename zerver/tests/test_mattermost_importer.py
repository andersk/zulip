import filecmp
import logging
import os
from typing import Any, Dict, List

import ujson

from zerver.data_import.import_util import SubscriberHandler
from zerver.data_import.mattermost import (
    build_reactions,
    check_user_in_team,
    convert_channel_data,
    convert_huddle_data,
    convert_user_data,
    create_username_to_user_mapping,
    do_convert_data,
    generate_huddle_name,
    get_mentioned_user_ids,
    label_mirror_dummy_users,
    mattermost_data_file_to_dict,
    process_user,
    reset_mirror_dummy_users,
    write_emoticon_data,
)
from zerver.data_import.mattermost_user import UserHandler
from zerver.data_import.sequencer import IdMapper
from zerver.lib.emoji import name_to_codepoint
from zerver.lib.import_realm import do_import_realm
from zerver.lib.test_classes import ZulipTestCase
from zerver.models import Message, Reaction, Recipient, UserProfile, get_realm, get_user


class MatterMostImporter(ZulipTestCase):
    logger = logging.getLogger()
    # set logger to a higher level to suppress 'logger.INFO' outputs
    logger.setLevel(logging.WARNING)

    def test_mattermost_data_file_to_dict(self) -> None:
        fixture_file_name = self.fixture_file_name("export.json", "mattermost_fixtures")
        mattermost_data = mattermost_data_file_to_dict(fixture_file_name)
        self.assertEqual(len(mattermost_data), 7)

        self.assertEqual(mattermost_data["version"], [1])

        self.assertEqual(len(mattermost_data["team"]), 2)
        self.assertEqual(mattermost_data["team"][0]["name"], "gryffindor")

        self.assertEqual(len(mattermost_data["channel"]), 5)
        self.assertEqual(mattermost_data["channel"][0]["name"], "gryffindor-common-room")
        self.assertEqual(mattermost_data["channel"][0]["team"], "gryffindor")

        self.assertEqual(len(mattermost_data["user"]), 5)
        self.assertEqual(mattermost_data["user"][1]["username"], "harry")
        self.assertEqual(len(mattermost_data["user"][1]["teams"]), 1)

        self.assertEqual(len(mattermost_data["post"]["channel_post"]), 20)
        self.assertEqual(mattermost_data["post"]["channel_post"][0]["team"], "gryffindor")
        self.assertEqual(mattermost_data["post"]["channel_post"][0]["channel"], "dumbledores-army")
        self.assertEqual(mattermost_data["post"]["channel_post"][0]["user"], "harry")
        self.assertEqual(len(mattermost_data["post"]["channel_post"][0]["replies"]), 1)

        self.assertEqual(len(mattermost_data["emoji"]), 2)
        self.assertEqual(mattermost_data["emoji"][0]["name"], "peerdium")

        fixture_file_name = self.fixture_file_name("export.json", "mattermost_fixtures/direct_channel")
        mattermost_data = mattermost_data_file_to_dict(fixture_file_name)

        self.assertEqual(len(mattermost_data["post"]["channel_post"]), 4)
        self.assertEqual(mattermost_data["post"]["channel_post"][0]["team"], "gryffindor")
        self.assertEqual(mattermost_data["post"]["channel_post"][0]["channel"], "gryffindor-common-room")
        self.assertEqual(mattermost_data["post"]["channel_post"][0]["user"], "ron")
        self.assertEqual(mattermost_data["post"]["channel_post"][0]["replies"], None)

        self.assertEqual(len(mattermost_data["post"]["direct_post"]), 7)
        self.assertEqual(mattermost_data["post"]["direct_post"][0]["user"], "ron")
        self.assertEqual(mattermost_data["post"]["direct_post"][0]["replies"], None)
        self.assertEqual(mattermost_data["post"]["direct_post"][0]["message"], "hey harry")
        self.assertEqual(mattermost_data["post"]["direct_post"][0]["channel_members"], ["ron", "harry"])

    def test_process_user(self) -> None:
        user_id_mapper = IdMapper()
        fixture_file_name = self.fixture_file_name("export.json", "mattermost_fixtures")
        mattermost_data = mattermost_data_file_to_dict(fixture_file_name)
        username_to_user = create_username_to_user_mapping(mattermost_data["user"])
        reset_mirror_dummy_users(username_to_user)

        harry_dict = username_to_user["harry"]
        harry_dict["is_mirror_dummy"] = False

        realm_id = 3

        team_name = "gryffindor"
        user = process_user(harry_dict, realm_id, team_name, user_id_mapper)
        self.assertEqual(user["avatar_source"], "G")
        self.assertEqual(user["delivery_email"], "harry@zulip.com")
        self.assertEqual(user["email"], "harry@zulip.com")
        self.assertEqual(user["full_name"], "Harry Potter")
        self.assertEqual(user["id"], 1)
        self.assertEqual(user["is_active"], True)
        self.assertEqual(user["role"], UserProfile.ROLE_REALM_ADMINISTRATOR)
        self.assertEqual(user["is_mirror_dummy"], False)
        self.assertEqual(user["realm"], 3)
        self.assertEqual(user["short_name"], "harry")
        self.assertEqual(user["timezone"], "UTC")

        # A user with a `null` team value shouldn't be an admin.
        harry_dict["teams"] = None
        user = process_user(harry_dict, realm_id, team_name, user_id_mapper)
        self.assertEqual(user["role"], UserProfile.ROLE_MEMBER)

        team_name = "slytherin"
        snape_dict = username_to_user["snape"]
        snape_dict["is_mirror_dummy"] = True
        user = process_user(snape_dict, realm_id, team_name, user_id_mapper)
        self.assertEqual(user["avatar_source"], "G")
        self.assertEqual(user["delivery_email"], "snape@zulip.com")
        self.assertEqual(user["email"], "snape@zulip.com")
        self.assertEqual(user["full_name"], "Severus Snape")
        self.assertEqual(user["id"], 2)
        self.assertEqual(user["is_active"], False)
        self.assertEqual(user["role"], UserProfile.ROLE_MEMBER)
        self.assertEqual(user["is_mirror_dummy"], True)
        self.assertEqual(user["realm"], 3)
        self.assertEqual(user["short_name"], "snape")
        self.assertEqual(user["timezone"], "UTC")

    def test_convert_user_data(self) -> None:
        user_id_mapper = IdMapper()
        realm_id = 3
        fixture_file_name = self.fixture_file_name("export.json", "mattermost_fixtures")
        mattermost_data = mattermost_data_file_to_dict(fixture_file_name)
        username_to_user = create_username_to_user_mapping(mattermost_data["user"])
        reset_mirror_dummy_users(username_to_user)

        team_name = "gryffindor"
        user_handler = UserHandler()
        convert_user_data(user_handler, user_id_mapper, username_to_user, realm_id, team_name)
        self.assertEqual(len(user_handler.get_all_users()), 2)
        self.assertTrue(user_id_mapper.has("harry"))
        self.assertTrue(user_id_mapper.has("ron"))
        self.assertEqual(user_handler.get_user(user_id_mapper.get("harry"))["full_name"], "Harry Potter")
        self.assertEqual(user_handler.get_user(user_id_mapper.get("ron"))["full_name"], "Ron Weasley")

        team_name = "slytherin"
        user_handler = UserHandler()
        convert_user_data(user_handler, user_id_mapper, username_to_user, realm_id, team_name)
        self.assertEqual(len(user_handler.get_all_users()), 3)
        self.assertTrue(user_id_mapper.has("malfoy"))
        self.assertTrue(user_id_mapper.has("pansy"))
        self.assertTrue(user_id_mapper.has("snape"))

        team_name = "gryffindor"
        # Snape is a mirror dummy user in Harry's team.
        label_mirror_dummy_users(2, team_name, mattermost_data, username_to_user)
        user_handler = UserHandler()
        convert_user_data(user_handler, user_id_mapper, username_to_user, realm_id, team_name)
        self.assertEqual(len(user_handler.get_all_users()), 3)
        self.assertTrue(user_id_mapper.has("snape"))

        team_name = "slytherin"
        user_handler = UserHandler()
        convert_user_data(user_handler, user_id_mapper, username_to_user, realm_id, team_name)
        self.assertEqual(len(user_handler.get_all_users()), 3)

    def test_convert_channel_data(self) -> None:
        fixture_file_name = self.fixture_file_name("export.json", "mattermost_fixtures")
        mattermost_data = mattermost_data_file_to_dict(fixture_file_name)
        username_to_user = create_username_to_user_mapping(mattermost_data["user"])
        reset_mirror_dummy_users(username_to_user)

        user_handler = UserHandler()
        subscriber_handler = SubscriberHandler()
        stream_id_mapper = IdMapper()
        user_id_mapper = IdMapper()
        team_name = "gryffindor"

        convert_user_data(
            user_handler=user_handler,
            user_id_mapper=user_id_mapper,
            user_data_map=username_to_user,
            realm_id=3,
            team_name=team_name,
        )

        zerver_stream = convert_channel_data(
            channel_data=mattermost_data["channel"],
            user_data_map=username_to_user,
            subscriber_handler=subscriber_handler,
            stream_id_mapper=stream_id_mapper,
            user_id_mapper=user_id_mapper,
            realm_id=3,
            team_name=team_name,
        )

        self.assertEqual(len(zerver_stream), 3)

        self.assertEqual(zerver_stream[0]["name"], "Gryffindor common room")
        self.assertEqual(zerver_stream[0]["invite_only"], False)
        self.assertEqual(zerver_stream[0]["description"], "A place for talking about Gryffindor common room")
        self.assertEqual(zerver_stream[0]["rendered_description"], "")
        self.assertEqual(zerver_stream[0]["realm"], 3)

        self.assertEqual(zerver_stream[1]["name"], "Gryffindor quidditch team")
        self.assertEqual(zerver_stream[1]["invite_only"], False)
        self.assertEqual(zerver_stream[1]["description"], "A place for talking about Gryffindor quidditch team")
        self.assertEqual(zerver_stream[1]["rendered_description"], "")
        self.assertEqual(zerver_stream[1]["realm"], 3)

        self.assertEqual(zerver_stream[2]["name"], "Dumbledores army")
        self.assertEqual(zerver_stream[2]["invite_only"], True)
        self.assertEqual(zerver_stream[2]["description"], "A place for talking about Dumbledores army")
        self.assertEqual(zerver_stream[2]["rendered_description"], "")
        self.assertEqual(zerver_stream[2]["realm"], 3)

        self.assertTrue(stream_id_mapper.has("gryffindor-common-room"))
        self.assertTrue(stream_id_mapper.has("gryffindor-quidditch-team"))
        self.assertTrue(stream_id_mapper.has("dumbledores-army"))

        # TODO: Add ginny
        ron_id = user_id_mapper.get("ron")
        harry_id = user_id_mapper.get("harry")
        self.assertEqual({ron_id, harry_id}, {1, 2})
        self.assertEqual(
            subscriber_handler.get_users(stream_id=stream_id_mapper.get("gryffindor-common-room")), {ron_id, harry_id},
        )
        self.assertEqual(
            subscriber_handler.get_users(stream_id=stream_id_mapper.get("gryffindor-quidditch-team")),
            {ron_id, harry_id},
        )
        self.assertEqual(
            subscriber_handler.get_users(stream_id=stream_id_mapper.get("dumbledores-army")), {ron_id, harry_id},
        )

        # Converting channel data when a user's `teams` value is `null`.
        username_to_user["ron"].update({"teams": None})
        zerver_stream = convert_channel_data(
            channel_data=mattermost_data["channel"],
            user_data_map=username_to_user,
            subscriber_handler=subscriber_handler,
            stream_id_mapper=stream_id_mapper,
            user_id_mapper=user_id_mapper,
            realm_id=3,
            team_name=team_name,
        )
        harry_id = user_id_mapper.get("harry")
        self.assertIn(harry_id, {1, 2})
        self.assertEqual(
            subscriber_handler.get_users(stream_id=stream_id_mapper.get("gryffindor-common-room")), {harry_id},
        )
        self.assertEqual(
            subscriber_handler.get_users(stream_id=stream_id_mapper.get("gryffindor-quidditch-team")), {harry_id},
        )
        self.assertEqual(subscriber_handler.get_users(stream_id=stream_id_mapper.get("dumbledores-army")), {harry_id})

        team_name = "slytherin"
        zerver_stream = convert_channel_data(
            channel_data=mattermost_data["channel"],
            user_data_map=username_to_user,
            subscriber_handler=subscriber_handler,
            stream_id_mapper=stream_id_mapper,
            user_id_mapper=user_id_mapper,
            realm_id=4,
            team_name=team_name,
        )

        malfoy_id = user_id_mapper.get("malfoy")
        pansy_id = user_id_mapper.get("pansy")
        snape_id = user_id_mapper.get("snape")
        self.assertEqual({malfoy_id, pansy_id, snape_id}, {3, 4, 5})
        self.assertEqual(
            subscriber_handler.get_users(stream_id=stream_id_mapper.get("slytherin-common-room")),
            {malfoy_id, pansy_id, snape_id},
        )
        self.assertEqual(
            subscriber_handler.get_users(stream_id=stream_id_mapper.get("slytherin-quidditch-team")),
            {malfoy_id, pansy_id},
        )

    def test_convert_huddle_data(self) -> None:
        fixture_file_name = self.fixture_file_name("export.json", "mattermost_fixtures/direct_channel")
        mattermost_data = mattermost_data_file_to_dict(fixture_file_name)
        username_to_user = create_username_to_user_mapping(mattermost_data["user"])
        reset_mirror_dummy_users(username_to_user)

        user_handler = UserHandler()
        subscriber_handler = SubscriberHandler()
        huddle_id_mapper = IdMapper()
        user_id_mapper = IdMapper()
        team_name = "gryffindor"

        convert_user_data(
            user_handler=user_handler,
            user_id_mapper=user_id_mapper,
            user_data_map=username_to_user,
            realm_id=3,
            team_name=team_name,
        )

        zerver_huddle = convert_huddle_data(
            huddle_data=mattermost_data["direct_channel"],
            user_data_map=username_to_user,
            subscriber_handler=subscriber_handler,
            huddle_id_mapper=huddle_id_mapper,
            user_id_mapper=user_id_mapper,
            realm_id=3,
            team_name=team_name,
        )

        self.assertEqual(len(zerver_huddle), 1)
        huddle_members = mattermost_data["direct_channel"][1]["members"]
        huddle_name = generate_huddle_name(huddle_members)

        self.assertTrue(huddle_id_mapper.has(huddle_name))
        self.assertEqual(subscriber_handler.get_users(huddle_id=huddle_id_mapper.get(huddle_name)), {1, 2, 3})

    def test_write_emoticon_data(self) -> None:
        fixture_file_name = self.fixture_file_name("export.json", "mattermost_fixtures")
        mattermost_data = mattermost_data_file_to_dict(fixture_file_name)
        output_dir = self.make_import_output_dir("mattermost")
        zerver_realm_emoji = write_emoticon_data(
            realm_id=3,
            custom_emoji_data=mattermost_data["emoji"],
            data_dir=self.fixture_file_name("", "mattermost_fixtures"),
            output_dir=output_dir,
        )
        self.assertEqual(len(zerver_realm_emoji), 2)
        self.assertEqual(zerver_realm_emoji[0]["file_name"], "peerdium")
        self.assertEqual(zerver_realm_emoji[0]["realm"], 3)
        self.assertEqual(zerver_realm_emoji[0]["deactivated"], False)

        self.assertEqual(zerver_realm_emoji[1]["file_name"], "tick")
        self.assertEqual(zerver_realm_emoji[1]["realm"], 3)
        self.assertEqual(zerver_realm_emoji[1]["deactivated"], False)

        records_file = os.path.join(output_dir, "emoji", "records.json")
        with open(records_file) as f:
            records_json = ujson.load(f)

        self.assertEqual(records_json[0]["file_name"], "peerdium")
        self.assertEqual(records_json[0]["realm_id"], 3)
        exported_emoji_path = self.fixture_file_name(mattermost_data["emoji"][0]["image"], "mattermost_fixtures")
        self.assertTrue(filecmp.cmp(records_json[0]["path"], exported_emoji_path))

        self.assertEqual(records_json[1]["file_name"], "tick")
        self.assertEqual(records_json[1]["realm_id"], 3)
        exported_emoji_path = self.fixture_file_name(mattermost_data["emoji"][1]["image"], "mattermost_fixtures")
        self.assertTrue(filecmp.cmp(records_json[1]["path"], exported_emoji_path))

    def test_get_mentioned_user_ids(self) -> None:
        user_id_mapper = IdMapper()
        harry_id = user_id_mapper.get("harry")

        raw_message = {
            "content": "Hello @harry",
        }
        ids = get_mentioned_user_ids(raw_message, user_id_mapper)
        self.assertEqual(list(ids), [harry_id])

        raw_message = {
            "content": "Hello",
        }
        ids = get_mentioned_user_ids(raw_message, user_id_mapper)
        self.assertEqual(list(ids), [])

        raw_message = {
            "content": "@harry How are you?",
        }
        ids = get_mentioned_user_ids(raw_message, user_id_mapper)
        self.assertEqual(list(ids), [harry_id])

        raw_message = {
            "content": "@harry @ron Where are you folks?",
        }
        ron_id = user_id_mapper.get("ron")
        ids = get_mentioned_user_ids(raw_message, user_id_mapper)
        self.assertEqual(list(ids), [harry_id, ron_id])

        raw_message = {
            "content": "@harry.com How are you?",
        }
        ids = get_mentioned_user_ids(raw_message, user_id_mapper)
        self.assertEqual(list(ids), [])

        raw_message = {
            "content": "hello@harry.com How are you?",
        }
        ids = get_mentioned_user_ids(raw_message, user_id_mapper)
        self.assertEqual(list(ids), [])

        harry_id = user_id_mapper.get("harry_")
        raw_message = {
            "content": "Hello @harry_",
        }
        ids = get_mentioned_user_ids(raw_message, user_id_mapper)
        self.assertEqual(list(ids), [harry_id])

        harry_id = user_id_mapper.get("harry.")
        raw_message = {
            "content": "Hello @harry.",
        }
        ids = get_mentioned_user_ids(raw_message, user_id_mapper)
        self.assertEqual(list(ids), [harry_id])

        harry_id = user_id_mapper.get("ha_rry.")
        raw_message = {
            "content": "Hello @ha_rry.",
        }
        ids = get_mentioned_user_ids(raw_message, user_id_mapper)
        self.assertEqual(list(ids), [harry_id])

        ron_id = user_id_mapper.get("ron")
        raw_message = {
            "content": "Hello @ron.",
        }
        ids = get_mentioned_user_ids(raw_message, user_id_mapper)
        self.assertEqual(list(ids), [])

        raw_message = {
            "content": "Hello @ron_",
        }
        ids = get_mentioned_user_ids(raw_message, user_id_mapper)
        self.assertEqual(list(ids), [])

    def test_check_user_in_team(self) -> None:
        fixture_file_name = self.fixture_file_name("export.json", "mattermost_fixtures")
        mattermost_data = mattermost_data_file_to_dict(fixture_file_name)
        username_to_user = create_username_to_user_mapping(mattermost_data["user"])
        reset_mirror_dummy_users(username_to_user)

        harry = username_to_user["harry"]
        self.assertTrue(check_user_in_team(harry, "gryffindor"))
        self.assertFalse(check_user_in_team(harry, "slytherin"))

        snape = username_to_user["snape"]
        self.assertFalse(check_user_in_team(snape, "gryffindor"))
        self.assertTrue(check_user_in_team(snape, "slytherin"))

        snape.update({"teams": None})
        self.assertFalse(check_user_in_team(snape, "slytherin"))

    def test_label_mirror_dummy_users(self) -> None:
        fixture_file_name = self.fixture_file_name("export.json", "mattermost_fixtures")
        mattermost_data = mattermost_data_file_to_dict(fixture_file_name)
        username_to_user = create_username_to_user_mapping(mattermost_data["user"])
        reset_mirror_dummy_users(username_to_user)

        label_mirror_dummy_users(
            num_teams=2, team_name="gryffindor", mattermost_data=mattermost_data, username_to_user=username_to_user,
        )
        self.assertFalse(username_to_user["harry"]["is_mirror_dummy"])
        self.assertFalse(username_to_user["ron"]["is_mirror_dummy"])
        self.assertFalse(username_to_user["malfoy"]["is_mirror_dummy"])

        # snape is mirror dummy since the user sent a message in gryffindor and
        # left the team
        self.assertTrue(username_to_user["snape"]["is_mirror_dummy"])

    def test_build_reactions(self) -> None:
        fixture_file_name = self.fixture_file_name("export.json", "mattermost_fixtures")
        mattermost_data = mattermost_data_file_to_dict(fixture_file_name)

        total_reactions: List[Dict[str, Any]] = []

        reactions = [
            {"user": "harry", "create_at": 1553165521410, "emoji_name": "tick"},
            {"user": "ron", "create_at": 1553166530805, "emoji_name": "smile"},
            {"user": "ron", "create_at": 1553166540953, "emoji_name": "world_map"},
            {"user": "harry", "create_at": 1553166540957, "emoji_name": "world_map"},
        ]

        zerver_realmemoji = write_emoticon_data(
            realm_id=3,
            custom_emoji_data=mattermost_data["emoji"],
            data_dir=self.fixture_file_name("", "mattermost_fixtures"),
            output_dir=self.make_import_output_dir("mattermost"),
        )

        # Make sure tick is present in fixture data
        self.assertEqual(zerver_realmemoji[1]["name"], "tick")
        tick_emoji_code = zerver_realmemoji[1]["id"]

        user_id_mapper = IdMapper()
        harry_id = user_id_mapper.get("harry")
        ron_id = user_id_mapper.get("ron")

        build_reactions(
            realm_id=3,
            total_reactions=total_reactions,
            reactions=reactions,
            message_id=5,
            user_id_mapper=user_id_mapper,
            zerver_realmemoji=zerver_realmemoji,
        )

        smile_emoji_code = name_to_codepoint["smile"]
        world_map_emoji_code = name_to_codepoint["world_map"]

        self.assertEqual(len(total_reactions), 4)
        self.assertEqual(
            self.get_set(total_reactions, "reaction_type"), {Reaction.REALM_EMOJI, Reaction.UNICODE_EMOJI},
        )
        self.assertEqual(self.get_set(total_reactions, "emoji_name"), {"tick", "smile", "world_map"})
        self.assertEqual(
            self.get_set(total_reactions, "emoji_code"), {tick_emoji_code, smile_emoji_code, world_map_emoji_code},
        )
        self.assertEqual(self.get_set(total_reactions, "user_profile"), {harry_id, ron_id})
        self.assertEqual(len(self.get_set(total_reactions, "id")), 4)
        self.assertEqual(len(self.get_set(total_reactions, "message")), 1)

    def team_output_dir(self, output_dir: str, team_name: str) -> str:
        return os.path.join(output_dir, team_name)

    def read_file(self, team_output_dir: str, output_file: str) -> Any:
        full_path = os.path.join(team_output_dir, output_file)
        with open(full_path) as f:
            return ujson.load(f)

    def test_do_convert_data(self) -> None:
        mattermost_data_dir = self.fixture_file_name("", "mattermost_fixtures")
        output_dir = self.make_import_output_dir("mattermost")

        do_convert_data(
            mattermost_data_dir=mattermost_data_dir, output_dir=output_dir, masking_content=False,
        )

        harry_team_output_dir = self.team_output_dir(output_dir, "gryffindor")
        self.assertEqual(os.path.exists(os.path.join(harry_team_output_dir, "avatars")), True)
        self.assertEqual(os.path.exists(os.path.join(harry_team_output_dir, "emoji")), True)
        self.assertEqual(os.path.exists(os.path.join(harry_team_output_dir, "attachment.json")), True)

        realm = self.read_file(harry_team_output_dir, "realm.json")

        self.assertEqual("Organization imported from Mattermost!", realm["zerver_realm"][0]["description"])

        exported_user_ids = self.get_set(realm["zerver_userprofile"], "id")
        exported_user_full_names = self.get_set(realm["zerver_userprofile"], "full_name")
        self.assertEqual({"Harry Potter", "Ron Weasley", "Severus Snape"}, exported_user_full_names)

        exported_user_emails = self.get_set(realm["zerver_userprofile"], "email")
        self.assertEqual({"harry@zulip.com", "ron@zulip.com", "snape@zulip.com"}, exported_user_emails)

        self.assertEqual(len(realm["zerver_stream"]), 3)
        exported_stream_names = self.get_set(realm["zerver_stream"], "name")
        self.assertEqual(
            exported_stream_names, {"Gryffindor common room", "Gryffindor quidditch team", "Dumbledores army"},
        )
        self.assertEqual(self.get_set(realm["zerver_stream"], "realm"), {realm["zerver_realm"][0]["id"]})
        self.assertEqual(self.get_set(realm["zerver_stream"], "deactivated"), {False})

        self.assertEqual(len(realm["zerver_defaultstream"]), 0)

        exported_recipient_ids = self.get_set(realm["zerver_recipient"], "id")
        self.assertEqual(len(exported_recipient_ids), 6)
        exported_recipient_types = self.get_set(realm["zerver_recipient"], "type")
        self.assertEqual(exported_recipient_types, {1, 2})
        exported_recipient_type_ids = self.get_set(realm["zerver_recipient"], "type_id")
        self.assertEqual(len(exported_recipient_type_ids), 3)

        exported_subscription_userprofile = self.get_set(realm["zerver_subscription"], "user_profile")
        self.assertEqual(len(exported_subscription_userprofile), 3)
        exported_subscription_recipients = self.get_set(realm["zerver_subscription"], "recipient")
        self.assertEqual(len(exported_subscription_recipients), 6)

        messages = self.read_file(harry_team_output_dir, "messages-000001.json")

        exported_messages_id = self.get_set(messages["zerver_message"], "id")
        self.assertIn(messages["zerver_message"][0]["sender"], exported_user_ids)
        self.assertIn(messages["zerver_message"][0]["recipient"], exported_recipient_ids)
        self.assertIn(messages["zerver_message"][0]["content"], "harry joined the channel.\n\n")

        exported_usermessage_userprofiles = self.get_set(messages["zerver_usermessage"], "user_profile")
        self.assertEqual(len(exported_usermessage_userprofiles), 3)
        exported_usermessage_messages = self.get_set(messages["zerver_usermessage"], "message")
        self.assertEqual(exported_usermessage_messages, exported_messages_id)

        do_import_realm(
            import_dir=harry_team_output_dir, subdomain="gryffindor",
        )
        realm = get_realm("gryffindor")

        self.assertFalse(get_user("harry@zulip.com", realm).is_mirror_dummy)
        self.assertFalse(get_user("ron@zulip.com", realm).is_mirror_dummy)
        self.assertTrue(get_user("snape@zulip.com", realm).is_mirror_dummy)

        messages = Message.objects.filter(sender__realm=realm)
        for message in messages:
            self.assertIsNotNone(message.rendered_content)

    def test_do_convert_data_with_direct_messages(self) -> None:
        mattermost_data_dir = self.fixture_file_name("direct_channel", "mattermost_fixtures")
        output_dir = self.make_import_output_dir("mattermost")

        do_convert_data(
            mattermost_data_dir=mattermost_data_dir, output_dir=output_dir, masking_content=False,
        )

        harry_team_output_dir = self.team_output_dir(output_dir, "gryffindor")
        self.assertEqual(os.path.exists(os.path.join(harry_team_output_dir, "avatars")), True)
        self.assertEqual(os.path.exists(os.path.join(harry_team_output_dir, "emoji")), True)
        self.assertEqual(os.path.exists(os.path.join(harry_team_output_dir, "attachment.json")), True)

        realm = self.read_file(harry_team_output_dir, "realm.json")

        self.assertEqual("Organization imported from Mattermost!", realm["zerver_realm"][0]["description"])

        exported_user_ids = self.get_set(realm["zerver_userprofile"], "id")
        exported_user_full_names = self.get_set(realm["zerver_userprofile"], "full_name")
        self.assertEqual({"Harry Potter", "Ron Weasley", "Ginny Weasley", "Tom Riddle"}, exported_user_full_names)

        exported_user_emails = self.get_set(realm["zerver_userprofile"], "email")
        self.assertEqual(
            {"harry@zulip.com", "ron@zulip.com", "ginny@zulip.com", "voldemort@zulip.com"}, exported_user_emails,
        )

        self.assertEqual(len(realm["zerver_stream"]), 3)
        exported_stream_names = self.get_set(realm["zerver_stream"], "name")
        self.assertEqual(
            exported_stream_names, {"Gryffindor common room", "Gryffindor quidditch team", "Dumbledores army"},
        )
        self.assertEqual(self.get_set(realm["zerver_stream"], "realm"), {realm["zerver_realm"][0]["id"]})
        self.assertEqual(self.get_set(realm["zerver_stream"], "deactivated"), {False})

        self.assertEqual(len(realm["zerver_defaultstream"]), 0)

        exported_recipient_ids = self.get_set(realm["zerver_recipient"], "id")
        self.assertEqual(len(exported_recipient_ids), 8)
        exported_recipient_types = self.get_set(realm["zerver_recipient"], "type")
        self.assertEqual(exported_recipient_types, {1, 2, 3})
        exported_recipient_type_ids = self.get_set(realm["zerver_recipient"], "type_id")
        self.assertEqual(len(exported_recipient_type_ids), 4)

        exported_subscription_userprofile = self.get_set(realm["zerver_subscription"], "user_profile")
        self.assertEqual(len(exported_subscription_userprofile), 4)
        exported_subscription_recipients = self.get_set(realm["zerver_subscription"], "recipient")
        self.assertEqual(len(exported_subscription_recipients), 8)

        messages = self.read_file(harry_team_output_dir, "messages-000001.json")

        exported_messages_id = self.get_set(messages["zerver_message"], "id")
        self.assertIn(messages["zerver_message"][0]["sender"], exported_user_ids)
        self.assertIn(messages["zerver_message"][0]["recipient"], exported_recipient_ids)
        self.assertIn(messages["zerver_message"][0]["content"], "ron joined the channel.\n\n")

        exported_usermessage_userprofiles = self.get_set(messages["zerver_usermessage"], "user_profile")
        self.assertEqual(len(exported_usermessage_userprofiles), 3)
        exported_usermessage_messages = self.get_set(messages["zerver_usermessage"], "message")
        self.assertEqual(exported_usermessage_messages, exported_messages_id)

        do_import_realm(
            import_dir=harry_team_output_dir, subdomain="gryffindor",
        )
        realm = get_realm("gryffindor")

        messages = Message.objects.filter(sender__realm=realm)
        for message in messages:
            self.assertIsNotNone(message.rendered_content)
        self.assertEqual(len(messages), 11)

        stream_messages = messages.filter(recipient__type=Recipient.STREAM).order_by("date_sent")
        stream_recipients = stream_messages.values_list("recipient", flat=True)
        self.assertEqual(len(stream_messages), 4)
        self.assertEqual(len(set(stream_recipients)), 2)
        self.assertEqual(stream_messages[0].sender.email, "ron@zulip.com")
        self.assertEqual(stream_messages[0].content, "ron joined the channel.\n\n")

        huddle_messages = messages.filter(recipient__type=Recipient.HUDDLE).order_by("date_sent")
        huddle_recipients = huddle_messages.values_list("recipient", flat=True)
        self.assertEqual(len(huddle_messages), 3)
        self.assertEqual(len(set(huddle_recipients)), 1)
        self.assertEqual(huddle_messages[0].sender.email, "ginny@zulip.com")
        self.assertEqual(huddle_messages[0].content, "Who is going to Hogesmead this weekend?\n\n")

        personal_messages = messages.filter(recipient__type=Recipient.PERSONAL).order_by("date_sent")
        personal_recipients = personal_messages.values_list("recipient", flat=True)
        self.assertEqual(len(personal_messages), 4)
        self.assertEqual(len(set(personal_recipients)), 3)
        self.assertEqual(personal_messages[0].sender.email, "ron@zulip.com")
        self.assertEqual(personal_messages[0].content, "hey harry\n\n")

    def test_do_convert_data_with_masking(self) -> None:
        mattermost_data_dir = self.fixture_file_name("", "mattermost_fixtures")
        output_dir = self.make_import_output_dir("mattermost")

        do_convert_data(
            mattermost_data_dir=mattermost_data_dir, output_dir=output_dir, masking_content=True,
        )

        harry_team_output_dir = self.team_output_dir(output_dir, "gryffindor")
        messages = self.read_file(harry_team_output_dir, "messages-000001.json")

        self.assertIn(messages["zerver_message"][0]["content"], "xxxxx xxxxxx xxx xxxxxxx.\n\n")

    def test_import_data_to_existing_database(self) -> None:
        mattermost_data_dir = self.fixture_file_name("", "mattermost_fixtures")
        output_dir = self.make_import_output_dir("mattermost")

        do_convert_data(
            mattermost_data_dir=mattermost_data_dir, output_dir=output_dir, masking_content=True,
        )

        harry_team_output_dir = self.team_output_dir(output_dir, "gryffindor")

        do_import_realm(
            import_dir=harry_team_output_dir, subdomain="gryffindor",
        )
        realm = get_realm("gryffindor")

        realm_users = UserProfile.objects.filter(realm=realm)
        messages = Message.objects.filter(sender__in=realm_users)
        for message in messages:
            self.assertIsNotNone(message.rendered_content)
