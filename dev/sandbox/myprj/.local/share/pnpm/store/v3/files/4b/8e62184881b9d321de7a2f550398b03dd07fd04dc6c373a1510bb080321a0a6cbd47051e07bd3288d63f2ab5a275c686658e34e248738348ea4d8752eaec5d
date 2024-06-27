"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Statement = void 0;
const format_error_1 = require("./utils/format-error");
/**
 * Promisified wrapper for the sqlite3#Statement interface.
 */
class Statement {
    constructor(stmt) {
        this.stmt = stmt;
    }
    /**
     * Returns the underlying sqlite3 Statement instance
     */
    getStatementInstance() {
        return this.stmt;
    }
    /**
     * Binds parameters to the prepared statement.
     *
     * Binding parameters with this function completely resets the statement object and row cursor
     * and removes all previously bound parameters, if any.
     */
    bind(...params) {
        return new Promise((resolve, reject) => {
            this.stmt.bind(...params, err => {
                if (err) {
                    return reject((0, format_error_1.formatError)(err));
                }
                resolve();
            });
        });
    }
    /**
     * Resets the row cursor of the statement and preserves the parameter bindings.
     * Use this function to re-execute the same query with the same bindings.
     */
    reset() {
        return new Promise(resolve => {
            this.stmt.reset(() => {
                resolve();
            });
        });
    }
    /**
     * Finalizes the statement. This is typically optional, but if you experience long delays before
     * the next query is executed, explicitly finalizing your statement might be necessary.
     * This might be the case when you run an exclusive query (see section Control Flow).
     * After the statement is finalized, all further function calls on that statement object
     * will throw errors.
     */
    finalize() {
        return new Promise((resolve, reject) => {
            this.stmt.finalize(err => {
                if (err) {
                    return reject((0, format_error_1.formatError)(err));
                }
                resolve();
            });
        });
    }
    /**
     * Binds parameters and executes the statement.
     *
     * If you specify bind parameters, they will be bound to the statement before it is executed.
     * Note that the bindings and the row cursor are reset when you specify even a single bind parameter.
     *
     * The execution behavior is identical to the Database#run method with the difference that the
     * statement will not be finalized after it is run. This means you can run it multiple times.
     *
     * @param {any} [params, ...] When the SQL statement contains placeholders, you
     * can pass them in here. They will be bound to the statement before it is
     * executed. There are three ways of passing bind parameters: directly in
     * the function's arguments, as an array, and as an object for named
     * parameters. This automatically sanitizes inputs.
     */
    run(...params) {
        return new Promise((resolve, reject) => {
            const stmt = this;
            this.stmt.run(...params, function (err) {
                if (err) {
                    return reject((0, format_error_1.formatError)(err));
                }
                resolve({
                    stmt,
                    lastID: this.lastID,
                    changes: this.changes
                });
            });
        });
    }
    /**
     * Binds parameters, executes the statement and retrieves the first result row.
     * The parameters are the same as the Statement#run function, with the following differences:
     *
     * Using this method can leave the database locked, as the database awaits further
     * calls to Statement#get to retrieve subsequent rows. To inform the database that you
     * are finished retrieving rows, you should either finalize (with Statement#finalize)
     * or reset (with Statement#reset) the statement.
     *
     * @param {any} [params, ...] When the SQL statement contains placeholders, you
     * can pass them in here. They will be bound to the statement before it is
     * executed. There are three ways of passing bind parameters: directly in
     * the function's arguments, as an array, and as an object for named
     * parameters. This automatically sanitizes inputs.
     */
    get(...params) {
        return new Promise((resolve, reject) => {
            this.stmt.get(...params, (err, row) => {
                if (err) {
                    return reject((0, format_error_1.formatError)(err));
                }
                resolve(row);
            });
        });
    }
    /**
     * Binds parameters, executes the statement and calls the callback with all result rows.
     * The parameters are the same as the Statement#run function, with the following differences:
     *
     * If the result set is empty, it will resolve to an empty array, otherwise it contains an
     * object for each result row which in turn contains the values of that row.
     * Like with Statement#run, the statement will not be finalized after executing this function.
     *
     * @param {any} [params, ...] When the SQL statement contains placeholders, you
     * can pass them in here. They will be bound to the statement before it is
     * executed. There are three ways of passing bind parameters: directly in
     * the function's arguments, as an array, and as an object for named
     * parameters. This automatically sanitizes inputs.
     *
     * @see https://github.com/mapbox/node-sqlite3/wiki/API#databaseallsql-param--callback
     */
    all(...params) {
        return new Promise((resolve, reject) => {
            this.stmt.all(...params, (err, rows) => {
                if (err) {
                    return reject((0, format_error_1.formatError)(err));
                }
                resolve(rows);
            });
        });
    }
    each(...params) {
        return new Promise((resolve, reject) => {
            const callback = params.pop();
            if (!callback || typeof callback !== 'function') {
                throw new Error('sqlite: Last param of Statement#each() must be a callback function');
            }
            if (params.length > 0) {
                const positional = params.pop();
                if (typeof positional === 'function') {
                    throw new Error('sqlite: Statement#each() should only have a single callback defined. See readme for usage.');
                }
                params.push(positional);
            }
            this.stmt.each(...params, (err, row) => {
                if (err) {
                    return callback((0, format_error_1.formatError)(err), null);
                }
                callback(null, row);
            }, (err, count) => {
                if (err) {
                    return reject((0, format_error_1.formatError)(err));
                }
                resolve(count);
            });
        });
    }
}
exports.Statement = Statement;
//# sourceMappingURL=Statement.js.map