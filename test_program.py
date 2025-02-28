import zmq

def add_game(socket, name, result):
    socket.send_json({"type": "game", "name": name, "result": result})
    print(socket.recv().decode())

def delete_player(socket, name):
    socket.send_json({"type": "delete", "name": name})
    print(socket.recv().decode())

def delete_all_players(socket):
    socket.send_json({"type": "delete-all"})
    print(socket.recv().decode())

def get_games(socket, name):
    socket.send_json({"type": "player", "name": name})
    response = socket.recv_json()
    if response["status"] == "success":
        print(response["games"])
    else:
        print(response["message"])


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5557")
    

if __name__ == "__main__":
    main()