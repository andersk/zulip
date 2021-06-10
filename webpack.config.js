const assets = require("./tools/webpack.assets.json");

module.exports = {
    mode: "production",
    context: __dirname,
    entry: assets,
};
