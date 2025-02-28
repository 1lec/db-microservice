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
    
    def get_player_id(self, name):
        """Receives a string representing the name of a player and returns the playerID, or returns None if the player
        is not in the database."""
        query = """
        SELECT playerID FROM Players
        WHERE name=?;
        """
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
    
    def add_player(self, name):
        """Receives a string representing the name of a player, and if the name is not already in the
        database, adds the name to the database."""
        # Verify name is not in the database
        if self.get_player_id(name): 
            return
        
        # Add name if not found in database
        query = """
        INSERT INTO Players (name) VALUES (
        ?
        );
        """
        self.cursor.execute(query, (name,))
        self.connection.commit()

    def delete_player(self, name):
        """Receives a string representing the name of a player, and if said name is present in the database,
        removes the name and all associated game results."""
        query = """
        DELETE FROM Players
        WHERE name=?;
        """
        self.cursor.execute(query, (name,))
        self.connection.commit()

    def add_game(self, playerID, result):
        query = """
        INSERT INTO Games (playerID, result) VALUES (
        ?,
        ?
        );
        """
        self.cursor.execute(query, (playerID, result))
        self.connection.commit()

    def listen(self):
        while True:
            request = self.socket.recv_json()
            request_type = request["type"]

            if request_type == "game":
                self.add_player(request["name"])
                player_id = self.get_player_id(request["name"])
                try:
                    self.add_game(player_id, request["result"])
                    self.socket.send_string("Result was successfully saved.")
                except:
                    self.socket.send_string("Failed to save game result.")
            if request_type == "delete":
                self.delete_player(request["name"])
                self.socket.send_string(f"Successfully deleted {request["name"]}.")

        self.connection.close()


def main():
    db = DatabaseManager()
    db.listen()


if __name__ == "__main__":
    main()