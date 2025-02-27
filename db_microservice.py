import sqlite3
import zmq


DATABASE_FILE = "monty_hall.db"
SCHEMA_FILE = "schema.sql"
ZMQ_PORT = "5557"


class DatabaseManager:
    """Handles all client requests and interacts with the database."""
    def __init__(self):
        self.connection = sqlite3.connect(DATABASE_FILE)
        self.cursor = self.connection.cursor()

    def add_game(self, gameID, playerID, result):
        game = f"""
        INSERT INTO Games VALUES(
        {gameID},
        {playerID},
        {result}
        );
        """
        self.cursor.execute(game)
        self.connection.commit()

    def listen(self):
        with open(SCHEMA_FILE) as schema_file:
            schema = schema_file.read()
            self.cursor.executescript(schema)

        self.connection.commit()
        self.connection.close()


def main():
    db = DatabaseManager()
    db.listen()


if __name__ == "__main__":
    main()