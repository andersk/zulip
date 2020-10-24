import path from "path";

import CssMinimizerPlugin from "css-minimizer-webpack-plugin";
import HtmlWebpackPlugin from "html-webpack-plugin";
import MiniCssExtractPlugin from "mini-css-extract-plugin";
import TerserPlugin from "terser-webpack-plugin";
import webpack from "webpack";
import BundleTracker from "webpack-bundle-tracker";

import DebugRequirePlugin from "./tools/debug-require-webpack-plugin";
import assets from "./tools/webpack.assets.json";

export default (_env: unknown, argv: {mode?: string}): webpack.Configuration[] => {
    const production: boolean = argv.mode === "production";

    const baseConfig: webpack.Configuration = {
        mode: production ? "production" : "development",
        context: __dirname,
        cache: {
            type: "filesystem",
            buildDependencies: {
                config: [__filename],
            },
        },
        snapshot: {
            immutablePaths: ["/srv/zulip-npm-cache"],
        },
    };

    const frontendConfig: webpack.Configuration = {
        ...baseConfig,
        name: "frontend",
        entry: production
            ? assets
            : Object.fromEntries(
                  Object.entries(assets).map(([name, paths]) => [
                      name,
                      [...paths, "./static/js/debug"],
                  ]),
              ),
        module: {
            rules: [
                {
                    test: require.resolve("./tools/debug-require"),
                    loader: "expose-loader",
                    options: {exposes: "require"},
                },
                {
                    test: require.resolve("jquery"),
                    loader: "expose-loader",
                    options: {exposes: ["$", "jQuery"]},
                },
                // Generate webfont
                {
                    test: /\.font\.js$/,
                    use: [
                        MiniCssExtractPlugin.loader,
                        {
                            loader: "css-loader",
                            options: {
                                url: false, // webfonts-loader generates public relative URLs
                            },
                        },
                        {
                            loader: "webfonts-loader",
                            options: {
                                fileName: production
                                    ? "files/[fontname].[chunkhash].[ext]"
                                    : "files/[fontname].[ext]",
                                publicPath: "",
                            },
                        },
                    ],
                },
                // Transpile .js and .ts files with Babel
                {
                    test: /\.(js|ts)$/,
                    include: [
                        path.resolve(__dirname, "static/shared/js"),
                        path.resolve(__dirname, "static/js"),
                    ],
                    loader: "babel-loader",
                },
                // Uses script-loader on minified files so we don't change global variables in them.
                // Also has the effect of making processing these files fast
                // Currently the source maps don't work with these so use unminified files
                // if debugging is required.
                {
                    // We dont want to match admin.js
                    test: /(\.min|min\.|zxcvbn)\.js/,
                    loader: "script-loader",
                },
                // regular css files
                {
                    test: /\.css$/,
                    exclude: path.resolve(__dirname, "static/styles"),
                    use: [
                        MiniCssExtractPlugin.loader,
                        {
                            loader: "css-loader",
                            options: {
                                sourceMap: true,
                            },
                        },
                    ],
                },
                // PostCSS loader
                {
                    test: /\.css$/,
                    include: path.resolve(__dirname, "static/styles"),
                    use: [
                        MiniCssExtractPlugin.loader,
                        {
                            loader: "css-loader",
                            options: {
                                importLoaders: 1,
                                sourceMap: true,
                            },
                        },
                        {
                            loader: "postcss-loader",
                            options: {
                                sourceMap: true,
                            },
                        },
                    ],
                },
                {
                    test: /\.hbs$/,
                    loader: "handlebars-loader",
                    options: {
                        // Tell webpack not to explicitly require these.
                        knownHelpers: [
                            "if",
                            "unless",
                            "each",
                            "with",
                            // The ones below are defined in static/js/templates.js
                            "plural",
                            "eq",
                            "and",
                            "or",
                            "not",
                            "t",
                            "tr",
                            "rendered_markdown",
                        ],
                        preventIndent: true,
                    },
                },
                // load fonts and files
                {
                    test: /\.(eot|jpg|svg|ttf|otf|png|woff2?)$/,
                    loader: "file-loader",
                    options: {
                        name: production ? "[name].[contenthash].[ext]" : "[path][name].[ext]",
                        outputPath: "files/",
                    },
                },
            ],
        },
        output: {
            path: path.resolve(__dirname, "static/webpack-bundles"),
            publicPath: "",
            filename: production ? "[name].[contenthash].js" : "[name].js",
            assetModuleFilename: production
                ? "files/[name].[hash][ext][query]"
                : "files/[path][name].[ext][query]",
            chunkFilename: production ? "[contenthash].js" : "[id].js",
        },
        resolve: {
            ...baseConfig.resolve,
            extensions: [".ts", ".js"],
        },
        // We prefer cheap-module-source-map over any eval-* options
        // because stacktrace-gps doesn't currently support extracting
        // the source snippets with the eval-* options.
        devtool: production ? "source-map" : "cheap-module-source-map",
        optimization: {
            minimizer: [
                new CssMinimizerPlugin({
                    sourceMap: true,
                    minify: (data, sourceMap) => {
                        // css-minimizer-webpack-plugin needs this require
                        // inside the function.
                        // eslint-disable-next-line @typescript-eslint/no-var-requires
                        const CleanCSS = require("clean-css");
                        const [[filename, styles]] = Object.entries(data);
                        const out = new CleanCSS({sourceMap: true}).minify({
                            [filename]: {styles, sourceMap},
                        });
                        return {css: out.styles, map: out.sourceMap, warnings: out.warnings};
                    },
                }),
                new TerserPlugin(),
            ],
            splitChunks: {
                chunks: "all",
                // webpack/examples/many-pages suggests 20 requests for HTTP/2
                maxAsyncRequests: 20,
                maxInitialRequests: 20,
            },
        },
        plugins: [
            new DebugRequirePlugin(),
            new BundleTracker({
                filename: production
                    ? "../../webpack-stats-production.json"
                    : "../../var/webpack-stats-dev.json",
                // Respecify many defaults until https://github.com/owais/webpack-bundle-tracker/pull/55 is merged
                path: path.resolve(__dirname, "static/webpack-bundles"),
                integrity: false,
                integrityHashes: [],
            }),
            ...(production
                ? []
                : [
                      // script-loader should load sourceURL in dev
                      new webpack.LoaderOptionsPlugin({debug: true}),
                  ]),
            // Extract CSS from files
            new MiniCssExtractPlugin({
                filename: production ? "[name].[contenthash].css" : "[name].css",
                chunkFilename: production ? "[contenthash].css" : "[id].css",
            }),
            new HtmlWebpackPlugin({
                filename: "5xx.html",
                template: "static/html/5xx.html",
                chunks: ["error-styles"],
            }),
        ],
        devServer: {
            clientLogLevel: "error",
            headers: {
                "Access-Control-Allow-Origin": "*",
            },
            publicPath: "/webpack/",
            stats: "errors-only",
        },
    };

    const serverConfig: webpack.Configuration = {
        ...baseConfig,
        name: "server",
        target: "node",
        entry: {
            "katex-cli": "shebang-loader!katex/cli",
        },
        output: {
            path: path.resolve(__dirname, "static/webpack-bundles"),
        },
    };

    return [frontendConfig, serverConfig];
};
