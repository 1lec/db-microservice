import sqlite3
import zmq


DATABASE_FILE = "monty_hall.db"
SCHEMA_FILE = "schema.sql"

def main():
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    with open(SCHEMA_FILE) as schema_file:
        schema = schema_file.read()
        cursor.executescript(schema)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    main()