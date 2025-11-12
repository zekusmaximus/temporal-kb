# kb/migrations/sqlite_to_postgres.py

import sqlite3
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
import json


def migrate_sqlite_to_postgres(sqlite_path: str, postgres_conn_string: str):
    """
    Migrate SQLite database to PostgreSQL

    Args:
        sqlite_path: Path to SQLite database
        postgres_conn_string: PostgreSQL connection string
            e.g., "postgresql://user:pass@host:5432/dbname"
    """

    print("Starting migration from SQLite to PostgreSQL...")

    # Connect to both databases
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row

    pg_conn = psycopg2.connect(postgres_conn_string)
    pg_cursor = pg_conn.cursor()

    # Get all table names from SQLite
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    tables = [row[0] for row in sqlite_cursor.fetchall()]

    print(f"Found {len(tables)} tables to migrate")

    for table in tables:
        print(f"\nMigrating table: {table}")

        # Get all rows from SQLite table
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()

        if not rows:
            print(f"  Skipping empty table: {table}")
            continue

        # Get column names
        columns = [description[0] for description in sqlite_cursor.description]

        # Prepare INSERT statement for PostgreSQL
        placeholders = ",".join(["%s"] * len(columns))
        insert_query = f"""
            INSERT INTO {table} ({','.join(columns)})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """

        # Convert rows to tuples
        data = [tuple(row) for row in rows]

        # Batch insert into PostgreSQL
        try:
            execute_values(pg_cursor, insert_query, data, page_size=1000)
            pg_conn.commit()
            print(f"  ✓ Migrated {len(data)} rows")
        except Exception as e:
            print(f"  ✗ Error migrating {table}: {e}")
            pg_conn.rollback()

    # Close connections
    sqlite_conn.close()
    pg_conn.close()

    print("\n✓ Migration complete!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python sqlite_to_postgres.py <sqlite_path> <postgres_conn_string>")
        sys.exit(1)

    migrate_sqlite_to_postgres(sys.argv[1], sys.argv[2])
