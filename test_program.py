import zmq


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5557")

    # Add a game
    socket.send_json({"type": "game", "name": "Eden", "result": 1})
    print(socket.recv().decode())

    # Get all results for a player
    socket.send_json({"type": "player", "name": "Eden"})
    response = socket.recv_json()
    if response["status"] == "success":
        print(response["games"])
    else:
        print(response["message"])

if __name__ == "__main__":
    main()