/// <reference types="./vendor-typings/sqlite3" />
import * as sqlite from 'sqlite3';
import { ISqlite } from './interfaces';
/**
 * Promisified wrapper for the sqlite3#Statement interface.
 */
export declare class Statement<S extends sqlite.Statement = sqlite.Statement> {
    stmt: S;
    constructor(stmt: S);
    /**
     * Returns the underlying sqlite3 Statement instance
     */
    getStatementInstance(): S;
    /**
     * Binds parameters to the prepared statement.
     *
     * Binding parameters with this function completely resets the statement object and row cursor
     * and removes all previously bound parameters, if any.
     */
    bind(...params: any[]): Promise<void>;
    /**
     * Resets the row cursor of the statement and preserves the parameter bindings.
     * Use this function to re-execute the same query with the same bindings.
     */
    reset(): Promise<void>;
    /**
     * Finalizes the statement. This is typically optional, but if you experience long delays before
     * the next query is executed, explicitly finalizing your statement might be necessary.
     * This might be the case when you run an exclusive query (see section Control Flow).
     * After the statement is finalized, all further function calls on that statement object
     * will throw errors.
     */
    finalize(): Promise<void>;
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
    run(...params: any[]): Promise<ISqlite.RunResult>;
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
    get<T = any>(...params: any[]): Promise<T | undefined>;
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
    all<T = any[]>(...params: any[]): Promise<T>;
    /**
     * Binds parameters, executes the statement and calls the callback for each result row.
     *
     * If the result set succeeds but is empty, the callback is never called.
     * In all other cases, the callback is called once for every retrieved row.
     * The order of calls correspond exactly to the order of rows in the result set.
     *
     * Like with Statement#run, the statement will not be finalized after executing this function.
     *
     * There is currently no way to abort execution!
     *
     * The last parameter to each() *must* be a callback function, where the first parameter will
     * be the returned row.
     *
     * @example await stmt.each('someParamValue', (err, row) => {
     *   // row contains the row data
     *   // each() resolves when there are no more rows to fetch
     * })
     *
     * @see https://github.com/mapbox/node-sqlite3/wiki/API#statementeachparam--callback-complete
     * @returns Promise<number> Number of rows returned
     */
    each<T = any>(callback: (err: any, row: T) => void): Promise<number>;
    each<T = any>(param1: any, callback: (err: any, row: T) => void): Promise<number>;
    each<T = any>(param1: any, param2: any, callback: (err: any, row: T) => void): Promise<number>;
    each<T = any>(param1: any, param2: any, param3: any, callback: (err: any, row: T) => void): Promise<number>;
    each<T = any>(...params: any[]): Promise<number>;
}
