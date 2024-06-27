"use strict";
/// <reference types="./vendor-typings/sqlite3" />
Object.defineProperty(exports, "__esModule", { value: true });
exports.Database = exports.Statement = exports.open = void 0;
const Statement_1 = require("./Statement");
Object.defineProperty(exports, "Statement", { enumerable: true, get: function () { return Statement_1.Statement; } });
const Database_1 = require("./Database");
Object.defineProperty(exports, "Database", { enumerable: true, get: function () { return Database_1.Database; } });
/**
 * Opens a database for manipulation. Most users will call this to get started.
 */
async function open(config) {
    const db = new Database_1.Database(config);
    await db.open();
    return db;
}
exports.open = open;
//# sourceMappingURL=index.js.map