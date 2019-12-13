import zmq


class Client(object):
    # port should be a system argument (sys.argv[#])
    # ip_file = ip_list.txt
    def __init__(self, port, ip_file):
        self.port = port
        self.file = ip_file

    # topic = what the message type is
    # message = message to be sent
    def send(self, message):
        leader_info = self.find_leader()
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://%s" % leader_info)
        socket.send_string(message)
        message = socket.recv_string()
        print(message)

    # For finding who the leader is
    def find_leader(self):
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind("tcp://*:%d" % self.port)
        topic = "1"
        message = "Find Leader"
        socket.send_string("%d|%s" % (topic, message))
        leader_info = self.receive()
        return leader_info

    # method ran after sending a request.
    # used to receive a response from servers
    def receive_leader_info(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)

        # To obtain all ip addresses from all servers
        ips = []
        with open(self.file) as f:
            for ip in f:
                # Remove http:// from the beginning of the ips
                ips.append(ip.strip(' http://'))

        # connect to all nodes and try to receive response message (only leader will send the response message)
        for ip in ips:
            socket.connect("tcp://%s" % ip)
        # topic_filter = 2 means response from leader telling client they are leader
        topic_filter = "2"
        socket.setsockopt_string(zmq.SUBSCRIBE, topic_filter)
        message = socket.recv_string()
        message_data = message.split('|')[1]    # to get message content (message = topic|message_data)
        return message_data


if __name__ == "__main__":
    if len(sys.argv) == 4:
        client_ip = sys.argv[1]
        txt_file = sys.argv[2]
        msg = sys.argv[3]
        client_port = client_ip.split(':')[2]
        c = Client(client_port, txt_file)
        c.send(msg)
    else:
        print("python client.py client_ip_address ip_list.txt message")
        print("client_ip_address format = http://ip:port")
