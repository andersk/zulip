const Handlebars = require("handlebars/dist/cjs/handlebars.js");
const path = require("path");
const { SourceMapConsumer, SourceNode } = require("source-map");

const templates_path = path.resolve(__dirname, "../../static/templates");

const hb = Handlebars.create();

class ZJavaScriptCompiler extends hb.JavaScriptCompiler {
    nameLookup(parent, name, type) {
        // Auto-register partials with relative paths, like handlebars-loader.
        if (type === "partial" && name !== "@partial-block") {
            const filename = path.resolve(path.dirname(this.options.srcName), name + ".hbs");
            return ["require(", JSON.stringify(filename), ")"];
        }
        return super.nameLookup(parent, name, type);
    }
}

ZJavaScriptCompiler.prototype.compiler = ZJavaScriptCompiler;
hb.JavaScriptCompiler = ZJavaScriptCompiler;

exports.process = (code, filename) => {
    const name = path.relative(templates_path, filename).slice(0, -".hbs".length);
    const pc = hb.precompile(code, { preventIndent: true, srcName: filename });
    const node = new SourceNode();
    node.add([
        "let hb, template;\n",
        "module.exports = (...args) => {\n",
        "    if (window.template_stub !== undefined) {\n",
        "        return window.template_stub(",
        JSON.stringify(name),
        ", ...args);\n",
        "    }\n",
        "    if (hb !== Handlebars) {\n",
        "        template = (hb = Handlebars).template(",
        SourceNode.fromStringWithSourceMap(pc.code, new SourceMapConsumer(pc.map)),
        ");\n",
        "    }\n",
        "    return template(...args);\n",
        "};\n",
    ]);
    const out = node.toStringWithSourceMap();
    return { code: out.code, map: out.map.toString() };
};
