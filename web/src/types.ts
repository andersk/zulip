import {z} from "zod";

// TODO/typescript: Move this to submessage.js
export type Submessage = {
    id: number;
    sender_id: number;
    message_id: number;
    content: string;
    msg_type: string;
};

// TODO/typescript: Move this to server_events
export type TopicLink = {
    text: string;
    url: string;
};

// TODO/typescript: Move this to server_events_dispatch
export type UserGroupUpdateEvent = {
    id: number;
    type: string;
    group_id: number;
    data: {
        name?: string;
        description?: string;
        can_mention_group?: number;
    };
};

// TODO/typescript: Move this to server_events
export type UpdateMessageEvent = {
    id: number;
    type: string;
    user_id: number | null;
    rendering_only: boolean;
    message_id: number;
    message_ids: number[];
    flags: string[];
    edit_timestamp: number;
    stream_name?: string;
    stream_id?: number;
    new_stream_id?: number;
    propagate_mode?: string;
    orig_subject?: string;
    subject?: string;
    topic_links?: TopicLink[];
    orig_content?: string;
    orig_rendered_content?: string;
    prev_rendered_content_version?: number;
    content?: string;
    rendered_content?: string;
    is_me_message?: boolean;
    // The server is still using subject.
    // This will not be set until it gets fixed.
    topic?: string;
};

// TODO/typescript: Move the User and Stream placeholder
// types to their appropriate modules.
export type User = Record<string, never>;

export const group_permission_setting_schema = z.object({
    require_system_group: z.boolean(),
    allow_internet_group: z.boolean(),
    allow_owners_group: z.boolean(),
    allow_nobody_group: z.boolean(),
    allow_everyone_group: z.boolean(),
    default_group_name: z.string(),
    id_field_name: z.string(),
    default_for_system_groups: z.nullable(z.string()),
    allowed_system_groups: z.array(z.string()),
});
export type GroupPermissionSetting = z.output<typeof group_permission_setting_schema>;

export const term_schema = z.object({
    negated: z.optional(z.boolean()),
    operator: z.string(),
    operand: z.string(),
});
export type Term = z.output<typeof term_schema>;
