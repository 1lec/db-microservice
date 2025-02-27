import zmq


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5557")

    socket.send_json({"type": "player", "name": "Alec"})
    print(socket.recv().decode())

    socket.send_json({"type": "game", "playerID": 1, "result": 0})
    print(socket.recv().decode())

    socket.send_json({"type": "get_id", "name": "Alec"})
    print("The playerID is:", socket.recv_json()["player_id"])

if __name__ == "__main__":
    main()