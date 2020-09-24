import SimpleBar from "simplebar";

import * as blueslip from "./blueslip";
import * as common from "./common";
import {localstorage} from "./localstorage";
import * as message_list from "./message_list";
import * as recent_senders from "./recent_senders";
import * as recent_topics from "./recent_topics";
import * as ui_report from "./ui_report";

// What, if anything, obscures the home tab?

export function replace_emoji_with_text(element) {
    element.find(".emoji").replaceWith(function () {
        if ($(this).is("img")) {
            return $(this).attr("alt");
        }
        return $(this).text();
    });
}

export function get_content_element(element_selector) {
    const element = element_selector.expectOne()[0];
    const sb = SimpleBar.instances.get(element);
    if (sb) {
        return $(sb.getContentElement());
    }
    return element_selector;
}

export function get_scroll_element(element_selector) {
    const element = element_selector.expectOne()[0];
    const sb = SimpleBar.instances.get(element);
    if (sb) {
        return $(sb.getScrollElement());
    } else if ("simplebar" in element.dataset) {
        // The SimpleBar mutation observer hasn’t processed this element yet.
        // Create the SimpleBar early in case we need to add event listeners.
        return $(new SimpleBar(element).getScrollElement());
    }
    return element_selector;
}

export function reset_scrollbar(element_selector) {
    const element = element_selector.expectOne()[0];
    const sb = SimpleBar.instances.get(element);
    if (sb) {
        sb.getScrollElement().scrollTop = 0;
    } else {
        element.scrollTop = 0;
    }
}

function update_message_in_all_views(message_id, callback) {
    for (const list of [message_list.all, home_msg_list, message_list.narrowed]) {
        if (list === undefined) {
            continue;
        }
        const row = list.get_row(message_id);
        if (row === undefined) {
            // The row may not exist, e.g. if you do an action on a message in
            // a narrowed view
            continue;
        }
        callback(row);
    }
}

export function show_error_for_unsupported_platform() {
    // Check if the user is using old desktop app
    if (typeof bridge !== "undefined") {
        // We don't internationalize this string because it is long,
        // and few users will have both the old desktop app and an
        // internationalized version of Zulip anyway.
        const error =
            "Hello! You're using the unsupported old Zulip desktop app," +
            " which is no longer developed. We recommend switching to the new, " +
            "modern desktop app, which you can download at " +
            "<a href='https://zulip.com/apps'>zulip.com/apps</a>.";

        ui_report.generic_embed_error(error);
    }
}

export function find_message(message_id) {
    // Try to find the message object. It might be in the narrow list
    // (if it was loaded when narrowed), or only in the message_list.all
    // (if received from the server while in a different narrow)
    let message;

    for (const msg_list of [message_list.all, home_msg_list, message_list.narrowed]) {
        if (msg_list !== undefined && message === undefined) {
            message = msg_list.get(message_id);
        }
    }

    return message;
}

export function update_starred_view(message_id, new_value) {
    const starred = new_value;

    // Avoid a full re-render, but update the star in each message
    // table in which it is visible.
    update_message_in_all_views(message_id, (row) => {
        const elt = row.find(".star");
        const star_container = row.find(".star_container");
        if (starred) {
            elt.addClass("fa-star").removeClass("fa-star-o");
            star_container.removeClass("empty-star");
        } else {
            elt.removeClass("fa-star").addClass("fa-star-o");
            star_container.addClass("empty-star");
        }
        const title_state = starred ? i18n.t("Unstar") : i18n.t("Star");
        elt.attr("title", i18n.t("__starred_status__ this message", {starred_status: title_state}));
    });
}

export function show_message_failed(message_id, failed_msg) {
    // Failed to send message, so display inline retry/cancel
    update_message_in_all_views(message_id, (row) => {
        const failed_div = row.find(".message_failed");
        failed_div.toggleClass("notvisible", false);
        failed_div.find(".failed_text").attr("title", failed_msg);
    });
}

export function remove_messages(message_ids) {
    const msg_ids_to_rerender = [];
    for (const list of [message_list.all, home_msg_list, message_list.narrowed]) {
        if (list === undefined) {
            continue;
        }
        for (const message_id of message_ids) {
            const row = list.get_row(message_id);
            if (row !== undefined) {
                msg_ids_to_rerender.push({id: message_id});
            }
        }
        list.remove_and_rerender(msg_ids_to_rerender);
    }
    recent_senders.update_topics_of_deleted_message_ids(message_ids);
    recent_topics.update_topics_of_deleted_message_ids(message_ids);
}

export function show_failed_message_success(message_id) {
    // Previously failed message succeeded
    update_message_in_all_views(message_id, (row) => {
        row.find(".message_failed").toggleClass("notvisible", true);
    });
}

export function get_hotkey_deprecation_notice(originalHotkey, replacementHotkey) {
    return i18n.t(
        'We\'ve replaced the "__originalHotkey__" hotkey with "__replacementHotkey__" ' +
            "to make this common shortcut easier to trigger.",
        {originalHotkey, replacementHotkey},
    );
}

let shown_deprecation_notices = [];

export function maybe_show_deprecation_notice(key) {
    let message;
    const isCmdOrCtrl = common.has_mac_keyboard() ? "Cmd" : "Ctrl";
    if (key === "C") {
        message = get_hotkey_deprecation_notice("C", "x");
    } else if (key === "*") {
        message = get_hotkey_deprecation_notice("*", isCmdOrCtrl + " + s");
    } else {
        blueslip.error("Unexpected deprecation notice for hotkey:", key);
        return;
    }

    // Here we handle the tracking for showing deprecation notices,
    // whether or not local storage is available.
    if (localstorage.supported()) {
        const notices_from_storage = JSON.parse(localStorage.getItem("shown_deprecation_notices"));
        if (notices_from_storage !== null) {
            shown_deprecation_notices = notices_from_storage;
        } else {
            shown_deprecation_notices = [];
        }
    }

    if (!shown_deprecation_notices.includes(key)) {
        $("#deprecation-notice-modal").modal("show");
        $("#deprecation-notice-message").text(message);
        $("#close-deprecation-notice").trigger("focus");
        shown_deprecation_notices.push(key);
        if (localstorage.supported()) {
            localStorage.setItem(
                "shown_deprecation_notices",
                JSON.stringify(shown_deprecation_notices),
            );
        }
    }
}

// Save the compose content cursor position and restore when we
// shift-tab back in (see hotkey.js).
let saved_compose_cursor = 0;

export function set_compose_textarea_handlers() {
    $("#compose-textarea").on("blur", function () {
        saved_compose_cursor = $(this).caret();
    });

    // on the end of the modified-message fade in, remove the fade-in-message class.
    const animationEnd = "webkitAnimationEnd oanimationend msAnimationEnd animationend";
    $("body").on(animationEnd, ".fade-in-message", function () {
        $(this).removeClass("fade-in-message");
    });
}

export function restore_compose_cursor() {
    $("#compose-textarea").trigger("focus").caret(saved_compose_cursor);
}

export function initialize() {
    set_compose_textarea_handlers();
    show_error_for_unsupported_platform();
}
