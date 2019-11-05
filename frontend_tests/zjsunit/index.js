const path = require('path');
const fs = require('fs');

global.assert = require('assert').strict;
global._ = require('underscore/underscore.js');
const _ = global._;

// Create a helper function to avoid sneaky delays in tests.
function immediate(f) {
    return () => {
        return f();
    };
}

// Set up our namespace helpers.
const namespace = require('./namespace.js');
global.set_global = namespace.set_global;
global.patch_builtin = namespace.set_global;
global.zrequire = namespace.zrequire;
global.stub_out_jquery = namespace.stub_out_jquery;
global.with_overrides = namespace.with_overrides;

global.window = global;
global.to_$ = () => window;

// Set up stub helpers.
const stub = require('./stub.js');
global.with_stub = stub.with_stub;

// Set up fake jQuery
global.make_zjquery = require('./zjquery.js').make_zjquery;

// Set up fake blueslip
global.make_zblueslip = require('./zblueslip.js').make_zblueslip;

// Set up fake translation
global.stub_i18n = require('./i18n.js');

// Set up Handlebars
global.make_handlebars = () => require("handlebars/dist/cjs/handlebars.runtime.js");
global.stub_templates = stub => {
    global.template_stub = stub;
};

const noop = function () {};

// Set up fixtures.
global.read_fixture_data = (fn) => {
    const full_fn = path.join(__dirname, '../../zerver/tests/fixtures/', fn);
    const data = JSON.parse(fs.readFileSync(full_fn, 'utf8', 'r'));
    return data;
};

// This could just be an alias for test(), except some of our tests were
// written under the assumption that the test body runs synchronously with the
// surrounding code.
global.run_test = (label, f) => {
    let dummy = () => {};
    try {
        f();
    } catch (err) {
        dummy = done => done(err);
    } finally {
        test(label, dummy);
    }
};

set_global('location', {
    hash: '#',
});
global.patch_builtin('setTimeout', noop);
global.patch_builtin('setInterval', noop);
_.throttle = immediate;
_.debounce = immediate;
