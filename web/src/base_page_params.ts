import $ from "jquery";
import {z} from "zod";

import {group_permission_setting_schema, term_schema} from "./types";

const t1 = performance.now();

// Sync this with zerver.context_processors.zulip_default_context
const default_params_schema = z.object({
    page_type: z.literal("default"),
    development_environment: z.boolean(),
    realm_sentry_key: z.optional(z.string()),
    request_language: z.string(),
    server_sentry_dsn: z.nullable(z.string()),
    server_sentry_environment: z.optional(z.string()),
    server_sentry_sample_rate: z.optional(z.number()),
    server_sentry_trace_rate: z.optional(z.number()),
});

// These parameters are sent in #page-params for both users and spectators.
//
// Sync this with zerver.lib.home.build_page_params_for_home_page_load
export const home_params_schema = default_params_schema.extend({
    page_type: z.literal("home"),
    apps_page_url: z.string(),
    bot_types: z.array(
        z.strictObject({
            type_id: z.number(),
            name: z.string(),
            allowed: z.boolean(),
        }),
    ),
    corporate_enabled: z.boolean(),
    furthest_read_time: z.nullable(z.number()),
    is_bot: z.optional(z.boolean()), // TODO: where is this sent?
    is_spectator: z.boolean(),
    language_list: z.array(
        z.strictObject({
            code: z.string(),
            locale: z.string(),
            name: z.string(),
            percent_translated: z.optional(z.number()),
        }),
    ),
    login_page: z.string(),
    narrow: z.optional(z.array(term_schema.strict())),
    narrow_stream: z.optional(z.string()),
    needs_tutorial: z.boolean(),
    promote_sponsoring_zulip: z.boolean(),
    show_billing: z.boolean(),
    show_plans: z.boolean(),
    show_webathena: z.boolean(),
    sponsorship_pending: z.boolean(),
    translation_data: z.record(z.string()),
});

// These parameters are sent in #page-params for users, but in the
// /json/register response for spectators.
//
// Sync this with zerver.lib.events.do_events_register
export const register_response_schema = z.object({
    avatar_source: z.string(),
    custom_profile_fields: z.array(
        z.strictObject({
            display_in_profile_summary: z.optional(z.boolean()),
            field_data: z.string(),
            hint: z.string(),
            id: z.number(),
            name: z.string(),
            order: z.number(),
            type: z.number(),
        }),
    ),
    delivery_email: z.string(),
    is_admin: z.boolean(),
    is_billing_admin: z.boolean(),
    is_guest: z.boolean(),
    is_moderator: z.boolean(),
    is_owner: z.boolean(),
    max_avatar_file_size_mib: z.number(),
    max_icon_file_size_mib: z.number(),
    max_logo_file_size_mib: z.number(),
    max_message_id: z.number(),
    muted_users: z.array(z.strictObject({id: z.number(), timestamp: z.number()})),
    realm_add_custom_emoji_policy: z.number(),
    realm_available_video_chat_providers: z.strictObject({
        disabled: z.strictObject({name: z.string(), id: z.number()}),
        jitsi_meet: z.strictObject({name: z.string(), id: z.number()}),
        zoom: z.optional(z.strictObject({name: z.string(), id: z.number()})),
        big_blue_button: z.optional(z.strictObject({name: z.string(), id: z.number()})),
    }),
    realm_avatar_changes_disabled: z.boolean(),
    realm_bot_domain: z.string(),
    realm_can_access_all_users_group: z.number(),
    realm_create_multiuse_invite_group: z.number(),
    realm_create_private_stream_policy: z.number(),
    realm_create_public_stream_policy: z.number(),
    realm_create_web_public_stream_policy: z.number(),
    realm_delete_own_message_policy: z.number(),
    realm_description: z.string(),
    realm_edit_topic_policy: z.number(),
    realm_email_changes_disabled: z.boolean(),
    realm_enable_guest_user_indicator: z.boolean(),
    realm_enable_spectator_access: z.boolean(),
    realm_icon_source: z.string(),
    realm_icon_url: z.string(),
    realm_invite_to_realm_policy: z.number(),
    realm_invite_to_stream_policy: z.number(),
    realm_is_zephyr_mirror_realm: z.boolean(),
    realm_jitsi_server_url: z.nullable(z.string()),
    realm_logo_source: z.string(),
    realm_logo_url: z.string(),
    realm_move_messages_between_streams_policy: z.number(),
    realm_name_changes_disabled: z.boolean(),
    realm_name: z.string(),
    realm_night_logo_source: z.string(),
    realm_night_logo_url: z.string(),
    realm_notifications_stream_id: z.number(),
    realm_org_type: z.number(),
    realm_plan_type: z.number(),
    realm_private_message_policy: z.number(),
    realm_push_notifications_enabled: z.boolean(),
    realm_upload_quota_mib: z.nullable(z.number()),
    realm_uri: z.string(),
    realm_user_group_edit_policy: z.number(),
    realm_video_chat_provider: z.number(),
    realm_waiting_period_threshold: z.number(),
    server_avatar_changes_disabled: z.boolean(),
    server_jitsi_server_url: z.nullable(z.string()),
    server_name_changes_disabled: z.boolean(),
    server_needs_upgrade: z.boolean(),
    server_presence_offline_threshold_seconds: z.number(),
    server_supported_permission_settings: z.strictObject({
        realm: z.record(group_permission_setting_schema.strict()),
        stream: z.record(group_permission_setting_schema.strict()),
        group: z.record(group_permission_setting_schema.strict()),
    }),
    server_web_public_streams_enabled: z.boolean(),
    user_id: z.optional(z.number()),
    zulip_merge_base: z.string(),
    zulip_plan_is_not_limited: z.boolean(),
    zulip_version: z.string(),
});

// Sync this with analytics.views.stats.render_stats
const stats_params_schema = default_params_schema.extend({
    page_type: z.literal("stats"),
    data_url_suffix: z.string(),
    for_installation: z.boolean(),
    remote: z.boolean(),
    upload_space_used: z.nullable(z.number()),
    guest_users: z.nullable(z.number()),
    translation_data: z.record(z.string()),
});

// Sync this with corporate.views.portico.team_view
const team_params_schema = default_params_schema.extend({
    page_type: z.literal("team"),
    contributors: z.unknown(),
});

// Sync this with corporate.lib.stripe.UpgradePageParams
const upgrade_params_schema = default_params_schema.extend({
    page_type: z.literal("upgrade"),
    annual_price: z.number(),
    demo_organization_scheduled_deletion_date: z.nullable(z.number()),
    monthly_price: z.number(),
    seat_count: z.number(),
    billing_base_url: z.string(),
    tier: z.number(),
    flat_discount: z.number(),
    flat_discounted_months: z.number(),
});

const loose_page_params_schema = z.union([
    default_params_schema,
    z.intersection(
        home_params_schema.passthrough(),
        register_response_schema.partial().passthrough(),
    ),
    stats_params_schema,
    team_params_schema,
    upgrade_params_schema,
]);

const page_params_schema = z.union([
    default_params_schema,
    z.intersection(home_params_schema.passthrough(), register_response_schema.passthrough()),
    stats_params_schema,
    team_params_schema,
    upgrade_params_schema,
]);

const loose_page_params: z.output<typeof loose_page_params_schema> = loose_page_params_schema.parse(
    $("#page-params").remove().data("params"),
);

// TODO/typescript: For spectators, some parameters are assigned later in
// ui_init.js. This cast pretends they're always available.
//
// eslint-disable-next-line @typescript-eslint/consistent-type-assertions
export const page_params = loose_page_params as z.output<typeof page_params_schema>;

const t2 = performance.now();
export const page_params_parse_time = t2 - t1;
