"use strict";

module.exports = {
    presets: ["@babel/typescript"],
    sourceType: "unambiguous",
    overrides: [
        {
            include: ["./static/shared/js", "./static/js"],
            presets: [
                [
                    "@babel/preset-env",
                    {
                        corejs: "3.6",
                        loose: true, // Loose mode for…of loops are 5× faster in Firefox
                        shippedProposals: true,
                        useBuiltIns: "usage",
                    },
                ],
            ],
        },
        {
            include: ["./webpack.config.ts", "./tools"],
            presets: [["@babel/preset-env", {targets: {node: "14"}}]],
        },
    ],
};
