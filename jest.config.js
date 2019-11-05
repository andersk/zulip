const escapeRegExp = require("lodash/escapeRegExp");

module.exports = {
    cacheDirectory: "<rootDir>/var/jest_rs",
    collectCoverageFrom: [
        "<rootDir>/static/**/*.{js,ts,hbs}",
        "!**/*.d.ts",
        "!<rootDir>/static/webpack-bundles/**",
    ],
    coverageDirectory: "<rootDir>/var/node-coverage",
    globalSetup: "<rootDir>/frontend_tests/zjsunit/global_setup.js",
    setupFilesAfterEnv: ["<rootDir>/frontend_tests/zjsunit/index.js"],
    testEnvironment: "node",
    testMatch: ["<rootDir>/frontend_tests/node_tests/*.{js,ts}"],
    transform: {
        ["^" +
        escapeRegExp(__dirname) +
        "(/static/js|/static/shared/js)/.*\\.(js|ts)$"]: "babel-jest",
        "\\.hbs$": "<rootDir>/frontend_tests/zjsunit/handlebars.js",
    },
};
