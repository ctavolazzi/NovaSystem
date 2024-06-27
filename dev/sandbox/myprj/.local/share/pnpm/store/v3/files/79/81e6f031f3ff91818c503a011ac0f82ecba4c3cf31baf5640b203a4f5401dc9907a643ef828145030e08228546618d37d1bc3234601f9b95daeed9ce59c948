import { Database } from '../Database';
import { IMigrate } from '../interfaces';
import MigrationParams = IMigrate.MigrationParams;
export declare function readMigrations(migrationPath?: string): Promise<IMigrate.MigrationData[]>;
/**
 * Migrates database schema to the latest version
 */
export declare function migrate(db: Database, config?: MigrationParams): Promise<void>;
