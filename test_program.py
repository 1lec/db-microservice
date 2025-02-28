import zmq


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5557")

    socket.send_json({"type": "game", "name": "Alec", "result": 1})
    print(socket.recv().decode())

    socket.send_json({"type": "delete", "name": "Alec"})
    print(socket.recv().decode())

if __name__ == "__main__":
    main()