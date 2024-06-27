"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.toSqlParams = void 0;
/**
 * Allows for using strings and `sql-template-strings`. Converts both to a
 * format that's usable by the SQL methods
 *
 * @param sql A SQL string or `sql-template-strings` object
 * @param params An array of parameters
 */
function toSqlParams(sql, params = []) {
    if (typeof sql === 'string') {
        return {
            sql,
            params
        };
    }
    return {
        sql: sql.sql,
        params: sql.values
    };
}
exports.toSqlParams = toSqlParams;
//# sourceMappingURL=strings.js.map