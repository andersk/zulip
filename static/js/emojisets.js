import {page_params} from "./page_params";

const emojisets = new Map([
    ["google", {css: google_css, sheet: google_sheet}],
    ["google-blob", {css: google_blob_css, sheet: google_blob_sheet}],
    ["twitter", {css: twitter_css, sheet: twitter_sheet}],
]);

// For `text` emojiset we fallback to `google-blob` emojiset
// for displaying emojis in emoji picker and typeahead.
emojisets.set("text", emojisets.get("google-blob"));

let current_emojiset;

export async function select(name) {
    const new_emojiset = emojisets.get(name);
    if (new_emojiset === current_emojiset) {
        return;
    }
    await new Promise((resolve, reject) => {
        const sheet = new Image();
        sheet.addEventListener("load", resolve);
        sheet.addEventListener("error", reject);
        sheet.src = new_emojiset.sheet;
    });
    if (current_emojiset) {
        current_emojiset.css.unuse();
    }
    new_emojiset.css.use();
    current_emojiset = new_emojiset;
}

export function initialize() {
    select(page_params.emojiset);

    // Load the octopus image in the background, so that the browser
    // will cache it for later use.  Note that we hardcode the octopus
    // emoji to the old Google one because it's better.
    //
    // TODO: We should probably just make this work just like the Zulip emoji.
    const octopus_image = new Image();
    octopus_image.src = octopus_url;
}
