export class FoldDict {
    constructor() {
        this._items = new Map();
    }
    get(key) {
        const mapping = this._items.get(this._munge(key));
        if (mapping === undefined) {
            return undefined;
        }
        return mapping.v;
    }
    set(key, value) {
        this._items.set(this._munge(key), {k: key, v: value});
        return this;
    }
    has(key) {
        return this._items.has(this._munge(key));
    }
    delete(key) {
        return this._items.delete(this._munge(key));
    }
    *keys() {
        for (const {k} of this._items.values()) {
            yield k;
        }
    }
    *values() {
        for (const {v} of this._items.values()) {
            yield v;
        }
    }
    *[Symbol.iterator]() {
        for (const {k, v} of this._items.values()) {
            yield [k, v];
        }
    }
    get size() {
        return this._items.size;
    }
    clear() {
        this._items.clear();
    }
    // Handle case-folding of keys and the empty string.
    _munge(key) {
        if (key === undefined) {
            throw new TypeError("Tried to call a FoldDict method with an undefined key.");
        }
        return key.toString().toLowerCase();
    }
}
