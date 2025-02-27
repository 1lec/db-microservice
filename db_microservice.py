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
        self.socket = self.zmq_connect(ZMQ_PORT)
        self.upload_schema()

    def upload_schema(self):
        """Creates a database if one does not already exists and populates it with tables from a schema."""
        with open(SCHEMA_FILE) as schema_file:
            schema = schema_file.read()
            self.cursor.executescript(schema)
        self.connection.commit()

    def zmq_connect(self, port):
        """Receives a port as a string and utilizes ZMQ to establish a connect through the port."""
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(f"tcp://*:{port}")
        return socket

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
        while True:
            request = self.socket.recv_json()
            request_type = request["type"]
            if request_type == "add":
                self.add_game(request["gameID"], request["playerID"], request["result"])
                self.socket.send_string("Successfully added row!")

        self.connection.close()


def main():
    db = DatabaseManager()
    db.listen()


if __name__ == "__main__":
    main()