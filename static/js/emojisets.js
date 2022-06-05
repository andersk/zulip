import google_blob_sheet from "emoji-datasource-google-blob/img/google/sheets-256/64.png";
import google_sheet from "emoji-datasource-google/img/google/sheets-256/64.png";
import twitter_sheet from "emoji-datasource-twitter/img/twitter/sheets-256/64.png";
import {Observable} from "rxjs";
import {distinctUntilChanged, switchMap} from "rxjs/operators";

import octopus_url from "../generated/emoji/images-google-64/1f419.png";

import {user_settings} from "./user_settings";

const emojisets = new Map([
    [
        "google",
        {
            css: () =>
                import(
                    "!style-loader?injectType=lazyStyleTag!css-loader!../generated/emoji-styles/google-sprite.css"
                ),
            sheet: google_sheet,
        },
    ],
    [
        "google-blob",
        {
            css: () =>
                import(
                    "!style-loader?injectType=lazyStyleTag!css-loader!../generated/emoji-styles/google-blob-sprite.css"
                ),
            sheet: google_blob_sheet,
        },
    ],
    [
        "twitter",
        {
            css: () =>
                import(
                    "!style-loader?injectType=lazyStyleTag!css-loader!../generated/emoji-styles/twitter-sprite.css"
                ),
            sheet: twitter_sheet,
        },
    ],
]);

// For `text` emoji set we fallback to `google-blob` emoji set
// for displaying emojis in emoji picker and typeahead.
emojisets.set("text", emojisets.get("google-blob"));

export let select;
let current_css;

new Observable((subscriber) => {
    select = (name) => {
        subscriber.next(name);
    };
})
    .pipe(distinctUntilChanged())
    .pipe(
        switchMap(async (name) => {
            const new_emojiset = emojisets.get(name);
            const [new_css] = await Promise.all([
                new_emojiset.css(),
                new Promise((resolve, reject) => {
                    const sheet = new Image();
                    sheet.addEventListener("load", resolve);
                    sheet.addEventListener("error", reject);
                    sheet.src = new_emojiset.sheet;
                }),
            ]);
            return new_css.default;
        }),
    )
    .subscribe((new_css) => {
        current_css?.unuse();
        new_css.use();
        current_css = new_css;
    });

export function initialize() {
    select(user_settings.emojiset);

    // Load the octopus image in the background, so that the browser
    // will cache it for later use.  Note that we hardcode the octopus
    // emoji to the old Google one because it's better.
    //
    // TODO: We should probably just make this work just like the Zulip emoji.
    const octopus_image = new Image();
    octopus_image.src = octopus_url;
}
