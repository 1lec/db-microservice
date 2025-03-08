import sqlite3
import zmq


DATABASE_FILE = "monty_hall.db"
SCHEMA_FILE = "schema.sql"
ZMQ_PORT = "5557"


class DatabaseManager:
    """Handles all client requests and interacts with the database."""
    def __init__(self):
        self.connection = sqlite3.connect(DATABASE_FILE)
        self.connection.execute("PRAGMA foreign_keys = ON;")  # Enable foreign key constraints
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
        print(f"Database Microservice is running and is listening on port {port}...")
        return socket
    
    def listen(self):
        """Continuously waits for, then handles requests from the client."""
        while True:
            request = self.socket.recv_json()
            print("Received request:", request)
            request_type = request["type"]

            if request_type == "game":
                self.insert_game(request)
            if request_type == "delete":
                self.delete_player(request["name"])
                self.socket.send_string(f"Successfully deleted {request["name"]}.")
            if request_type == "delete-all":
                try:
                    self.delete_all_players()
                    self.socket.send_string("Successfully deleted all names.")
                except:
                    self.socket.send_string("Failed to delete all names.")
            if request_type == "player":
                player_id = self.get_player_id(request["name"])
                if player_id:
                    games = self.get_games(player_id)
                    response = {"status": "success", "games": games}
                else:
                    response = {"status": "failure", "message": f"There were no games found for {request["name"]}."}
                self.socket.send_json(response)
            if request_type == "all-players":
                games = self.get_all_games()
                if games:
                    response = {"status": "success", "games": games}
                else:
                    response = {"status": "failure", "message": "There were no saved games found."}
                self.socket.send_json(response)

        self.connection.close()
    
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

    def delete_all_players(self):
        """Deletes all players and their associated game results from the database, essentially clearing the database."""
        query = """
        DELETE FROM Players;
        """
        self.cursor.execute(query)
        self.connection.commit()

    def insert_game(self, request):
        """Receives a request to insert a game into the database, adds the player to the database if needed,
        then inserts the game into the database."""
        self.add_player(request["name"])
        player_id = self.get_player_id(request["name"])
        try:
            query = """
            INSERT INTO Games (playerID, result) VALUES (
            ?,
            ?
            );
            """
            self.cursor.execute(query, (player_id, request["result"]))
            self.connection.commit()
            self.socket.send_string("Result was successfully saved.")
        except:
            self.socket.send_string("Failed to save game result.")

    def get_games(self, playerID):
        """Received a playerID and returns all games for that player."""
        query = """
        SELECT Players.name, Games.result FROM Games
        INNER JOIN Players ON Games.playerID=Players.playerID
        WHERE Games.playerID = ?;
        """
        self.cursor.execute(query, (playerID,))
        game_tuples = self.cursor.fetchall()
        game_lists = [list(game_tuple) for game_tuple in game_tuples]
        return game_lists
    
    def get_all_games(self):
        """Retrieves all games present in the database."""
        query = """
        SELECT Players.name, Games.result FROM Games
        INNER JOIN Players ON Games.playerID=Players.playerID
        """
        self.cursor.execute(query)
        game_tuples = self.cursor.fetchall()
        game_lists = [list(game_tuple) for game_tuple in game_tuples]
        return game_lists



def main():
    db = DatabaseManager()
    db.listen()


if __name__ == "__main__":
    main()