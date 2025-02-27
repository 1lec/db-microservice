import sqlite3
import zmq


DATABASE_FILE = "monty_hall.db"
SCHEMA_FILE = "schema.sql"


def add_game(cursor, gameID, playerID, result):
    game = f"""
    INSERT INTO Games VALUES(
    {gameID},
    {playerID},
    {result}
    );
    """
    cursor.execute(game)

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