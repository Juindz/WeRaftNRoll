import zmq

# port should be a system argument (sys.argv[#])
# zmq PUB will publish messages to all subscribers (no need to specify leader; leader will pick up message on its own)
class Client(object):
    def __init__(self, port, leader_ip=None):
        self.port = port
        leader_ip

    # topic = what the message type is
    # message = message to be sent
    def send(self, topic, message):
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind("tcp://*:%d" % self.port)
        socket.send("%d|%s" % (topic, message))

    # For finding who the leader is
    # def find_leader(self):
    #     context = zmq.Context()
    #     socket = context.socket(zmq.PUB)
    #     socket.bind("tcp://*:%d" % self.port)
    #     topic = 1
    #     message = "Find Leader"
    #     socket.send("%d|%s" % (topic, message))
    #     leader_ip = self.receive()

    # method ran after sending a request.
    # used to receive a response from servers
    def receive(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)

        # connect to all nodes and try to receive response message (only leader will send the response message)
        for node in num_nodes:
            socket.connect("tcp://%s:%d" % (node._ip, node._port))
        topic_filter = 2
        socket.setsockopt(zmq.SUBSCRIBE, topic_filter)
        message = socket.recv()
        message_data = message.split('|')[1]    # to get message content (message = topic|message_data)
        return message_data




