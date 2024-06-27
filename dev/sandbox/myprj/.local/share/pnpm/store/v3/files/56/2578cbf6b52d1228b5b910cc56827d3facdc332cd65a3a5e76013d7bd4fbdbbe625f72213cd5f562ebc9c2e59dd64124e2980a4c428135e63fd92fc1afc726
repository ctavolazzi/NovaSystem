"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Database = void 0;
const Statement_1 = require("./Statement");
const migrate_1 = require("./utils/migrate");
const strings_1 = require("./utils/strings");
const format_error_1 = require("./utils/format-error");
/**
 * Promisified wrapper for the sqlite3#Database interface.
 */
class Database {
    constructor(config) {
        this.config = config;
        this.db = null;
    }
    /**
     * Event handler when verbose mode is enabled.
     * @see https://github.com/mapbox/node-sqlite3/wiki/Debugging
     */
    on(event, listener) {
        this.db.on(event, listener);
    }
    /**
     * Returns the underlying sqlite3 Database instance
     */
    getDatabaseInstance() {
        return this.db;
    }
    /**
     * Opens the database
     */
    open() {
        return new Promise((resolve, reject) => {
            let { filename, mode, driver } = this.config;
            // https://github.com/mapbox/node-sqlite3/wiki/API#new-sqlite3databasefilename-mode-callback
            if (filename === null || filename === undefined) {
                throw new Error('sqlite: filename cannot be null / undefined');
            }
            if (!driver) {
                throw new Error('sqlite: driver is not defined');
            }
            if (mode) {
                this.db = new driver(filename, mode, err => {
                    if (err) {
                        return reject((0, format_error_1.formatError)(err));
                    }
                    resolve();
                });
            }
            else {
                this.db = new driver(filename, err => {
                    if (err) {
                        return reject((0, format_error_1.formatError)(err));
                    }
                    resolve();
                });
            }
        });
    }
    /**
     * Closes the database.
     */
    close() {
        return new Promise((resolve, reject) => {
            this.db.close(err => {
                if (err) {
                    return reject((0, format_error_1.formatError)(err));
                }
                resolve();
            });
        });
    }
    /**
     * @see https://github.com/mapbox/node-sqlite3/wiki/API#databaseconfigureoption-value
     */
    configure(option, value) {
        this.db.configure(option, value);
    }
    /**
     * Runs the SQL query with the specified parameters. It does not retrieve any result data.
     * The function returns the Database object for which it was called to allow for function chaining.
     *
     * @param {string} sql The SQL query to run.
     *
     * @param {any} [params, ...] When the SQL statement contains placeholders, you
     * can pass them in here. They will be bound to the statement before it is
     * executed. There are three ways of passing bind parameters: directly in
     * the function's arguments, as an array, and as an object for named
     * parameters. This automatically sanitizes inputs.
     *
     * @see https://github.com/mapbox/node-sqlite3/wiki/API#databaserunsql-param--callback
     */
    run(sql, ...params) {
        return new Promise((resolve, reject) => {
            const sqlObj = (0, strings_1.toSqlParams)(sql, params);
            this.db.run(sqlObj.sql, ...sqlObj.params, function (err) {
                if (err) {
                    return reject((0, format_error_1.formatError)(err));
                }
                resolve({
                    stmt: new Statement_1.Statement(this.stmt),
                    lastID: this.lastID,
                    changes: this.changes
                });
            });
        });
    }
    /**
     * Runs the SQL query with the specified parameters and resolves with
     * with the first result row afterwards. If the result set is empty, returns undefined.
     *
     * The property names correspond to the column names of the result set.
     * It is impossible to access them by column index; the only supported way is by column name.
     *
     * @param {string} sql The SQL query to run.
     *
     * @param {any} [params, ...] When the SQL statement contains placeholders, you
     * can pass them in here. They will be bound to the statement before it is
     * executed. There are three ways of passing bind parameters: directly in
     * the function's arguments, as an array, and as an object for named
     * parameters. This automatically sanitizes inputs.
     *
     * @see https://github.com/mapbox/node-sqlite3/wiki/API#databasegetsql-param--callback
     */
    get(sql, ...params) {
        return new Promise((resolve, reject) => {
            const sqlObj = (0, strings_1.toSqlParams)(sql, params);
            this.db.get(sqlObj.sql, ...sqlObj.params, (err, row) => {
                if (err) {
                    return reject((0, format_error_1.formatError)(err));
                }
                resolve(row);
            });
        });
    }
    each(sql, ...params) {
        return new Promise((resolve, reject) => {
            const callback = params.pop();
            if (!callback || typeof callback !== 'function') {
                throw new Error('sqlite: Last param of Database#each() must be a callback function');
            }
            if (params.length > 0) {
                const positional = params.pop();
                if (typeof positional === 'function') {
                    throw new Error('sqlite: Database#each() should only have a single callback defined. See readme for usage.');
                }
                params.push(positional);
            }
            const sqlObj = (0, strings_1.toSqlParams)(sql, params);
            this.db.each(sqlObj.sql, ...sqlObj.params, (err, row) => {
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
    /**
     * Runs the SQL query with the specified parameters. The parameters are the same as the
     * Database#run function, with the following differences:
     *
     * If the result set is empty, it will be an empty array, otherwise it will
     * have an object for each result row which
     * in turn contains the values of that row, like the Database#get function.
     *
     * Note that it first retrieves all result rows and stores them in memory.
     * For queries that have potentially large result sets, use the Database#each
     * function to retrieve all rows or Database#prepare followed by multiple
     * Statement#get calls to retrieve a previously unknown amount of rows.
     *
     * @param {string} sql The SQL query to run.
     *
     * @param {any} [params, ...] When the SQL statement contains placeholders, you
     * can pass them in here. They will be bound to the statement before it is
     * executed. There are three ways of passing bind parameters: directly in
     * the function's arguments, as an array, and as an object for named
     * parameters. This automatically sanitizes inputs.
     *
     * @see https://github.com/mapbox/node-sqlite3/wiki/API#databaseallsql-param--callback
     */
    all(sql, ...params) {
        return new Promise((resolve, reject) => {
            const sqlObj = (0, strings_1.toSqlParams)(sql, params);
            this.db.all(sqlObj.sql, ...sqlObj.params, (err, rows) => {
                if (err) {
                    return reject((0, format_error_1.formatError)(err));
                }
                resolve(rows);
            });
        });
    }
    /**
     * Runs all SQL queries in the supplied string. No result rows are retrieved. If a query fails,
     * no subsequent statements will be executed (wrap it in a transaction if you want all
     * or none to be executed).
     *
     * Note: This function will only execute statements up to the first NULL byte.
     * Comments are not allowed and will lead to runtime errors.
     *
     * @param {string} sql The SQL query to run.
     * @param {any} [params, ...] Same as the `params` parameter of `all`
     * @see https://github.com/mapbox/node-sqlite3/wiki/API#databaseexecsql-callback
     */
    exec(sql, ...params) {
        return new Promise((resolve, reject) => {
            const sqlObj = (0, strings_1.toSqlParams)(sql, params);
            this.db.exec(sqlObj.sql, err => {
                if (err) {
                    return reject((0, format_error_1.formatError)(err));
                }
                resolve();
            });
        });
    }
    /**
     * Prepares the SQL statement and optionally binds the specified parameters.
     * When bind parameters are supplied, they are bound to the prepared statement.
     *
     * @param {string} sql The SQL query to run.
     * @param {any} [params, ...] When the SQL statement contains placeholders, you
     * can pass them in here. They will be bound to the statement before it is
     * executed. There are three ways of passing bind parameters: directly in
     * the function's arguments, as an array, and as an object for named
     * parameters. This automatically sanitizes inputs.
     * @returns Promise<Statement> Statement object
     */
    prepare(sql, ...params) {
        return new Promise((resolve, reject) => {
            const sqlObj = (0, strings_1.toSqlParams)(sql, params);
            const stmt = this.db.prepare(sqlObj.sql, ...sqlObj.params, err => {
                if (err) {
                    return reject(err);
                }
                resolve(new Statement_1.Statement(stmt));
            });
        });
    }
    /**
     * Loads a compiled SQLite extension into the database connection object.
     *
     * @param {string} path Filename of the extension to load
     */
    loadExtension(path) {
        return new Promise((resolve, reject) => {
            this.db.loadExtension(path, err => {
                if (err) {
                    return reject((0, format_error_1.formatError)(err));
                }
                resolve();
            });
        });
    }
    /**
     * Performs a database migration.
     */
    async migrate(config) {
        await (0, migrate_1.migrate)(this, config);
    }
    /**
     * The methods underneath requires creative work to implement. PRs / proposals accepted!
     */
    /*
     * Unsure if serialize can be made into a promise.
     */
    serialize() {
        throw new Error('sqlite: Currently not implemented. Use getDatabaseInstance().serialize() instead.');
    }
    /*
     * Unsure if parallelize can be made into a promise.
     */
    parallelize() {
        throw new Error('sqlite: Currently not implemented. Use getDatabaseInstance().parallelize() instead.');
    }
}
exports.Database = Database;
//# sourceMappingURL=Database.js.map