import zmq


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5557")

    socket.send_json({"type": "add", "gameID": 1, "playerID": 1, "result": 0})
    print(socket.recv().decode())

    socket.send_json({"type": "add", "gameID": 2, "playerID": 2, "result": 1})
    print(socket.recv().decode())

    socket.send_json({"type": "add", "gameID": 3, "playerID": 1, "result": 0})
    print(socket.recv().decode())


if __name__ == "__main__":
    main()