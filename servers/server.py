import zmq
import threading
import time
import random
from collections import defaultdict
import sys
import pickle

from follower_on_message import follower_message
from candidate_on_message import candidate_message
from leader_on_message import leader_message
from boards import memory_board
from config import cfg
from message import messages

FOLLOWER = 0
CANDIDATE = 1
LEADER = 2

# Create a random timeout for each server in each term
def random_timeout():
    return random.randrange(cfg.LOW_TIMEOUT, cfg.HIGH_TIMEOUT) / 1000

class Server(object):

    def __init__(self, address, neighbors):
        self.address = address
        self.state = FOLLOWER
        self.log = []
        self.votes = []
        self.last_vote = None
        self.commit_table = []
        self.nextIndexes = {}
        self.matchIndex = {}
        self.messageBoard = memory_board.MemoryBoard()
        self.neighbors = neighbors
        self.lock = threading.Lock()
        self.majority = ((len(self.neighbors) + 1) // 2) + 1
        self.timeout_thread = None

        self.commitIndex = 0
        self.currentTerm = 0
        self.voteCount = 0

        self.lastApplied = 0

        self.lastLogIndex = 0
        self.lastLogTerm = None

        self.messageBoard.set_owner(self)
        # self.begin_init_timeout = False
        self.init_timeout()

        self.election_time = None

        self.logYesCountDict = {}
    #     add (index, 0)

    # Append the message to its messageBoard for sending.
    def send_message(self, receiver, message):
        if receiver in self.neighbors:
            message._receiver = receiver.address
            receiver.post_message(message)

    def send_message_response(self, message):
        n = [n for n in self.neighbors if n.address == message.receiver]
        if len(n) > 0:
            n[0].post_message(message)

    def post_message(self, message):
        self.messageBoard.post_message(message)

        # sender, receiver, term, success
    def send_response_message(self, msg, yes=True):
        response = messages.AppendEntryResponse(self.address, msg.sender, msg.term, yes)
        self.send_message_response(response)

    # According to the state of the server, redirect to the specific method.
    def on_message(self, message):
        print("enterServer")
        if message.term > self.currentTerm:
            self.currentTerm = message.term
        # Is the messages.term < ours? If so we need to tell
        #   them this so they don't get left behind.
        elif message.term < self.currentTerm:
            self.send_response_message(message, yes=False)
            return
        if self.state == FOLLOWER:
            follower_message(self, message)
        elif self.state == CANDIDATE:
            candidate_on_message.candidate_message(self, message)
        else:
            leader_on_message.leader_message(self, message)

    def reset_timeout(self):
        self.election_time = time.time() + random_timeout()

    # the timeout function
    def timeout_loop(self):
        # only stop timeout thread when winning the election
        while self.state != LEADER:
            self.votes = []
            self.voteCount = 0
            self.last_vote = None
            self.logYesCountDict = {}

            delta = self.election_time - time.time()
            if delta < 0:
                self.start_election()
            else:
                time.sleep(delta)

    # initiate timeout thread, or reset it
    def init_timeout(self):
        self.reset_timeout()
        # safety guarantee, timeout thread may expire after election
        if self.timeout_thread and self.timeout_thread.isAlive():
            return
        self.timeout_thread = threading.Thread(target=self.timeout_loop)
        self.timeout_thread.start()

    # increment only when we are candidate and receive positive vote
    # change status to LEADER and start heartbeat as soon as we reach majority
    def increment_vote(self):
        self.voteCount += 1
        s = self.address + " " + str(self.voteCount)
        print(s)
        if self.voteCount >= self.majority:
            print("{self.address} becomes the leader of term {self.currentTerm}")
            self.votes = []
            self.voteCount = 0
            self.state = LEADER
            self.nextIndexes = defaultdict(int)
            self.matchIndex = defaultdict(int)
            for n in self.neighbors:
                self.nextIndexes[n.address] = self.lastLogIndex + 1
                self.matchIndex[n.address] = 0
            self.start_heart_beat()

    # vote for myself, increase term, change status to candidate
    # reset the timeout and start sending request to followers
    def start_election(self):
        print("start election")
        self.currentTerm += 1
        self.voteCount = 0
        self.state = CANDIDATE
        self.init_timeout()
        self.increment_vote()
        self.send_vote_req()

    # spawn threads to request vote for all followers until get reply
    def send_vote_req(self):
        # TODO: use map later for better performance
        # we continue to ask to vote to the address that haven't voted yet
        # till everyone has voted
        # or I am the leader
        for voter in self.neighbors:
            threading.Thread(target=self.ask_for_vote,
                             args=(voter.address, self.currentTerm)).start()

    # request vote to other servers during given election term
    def ask_for_vote(self, voter, term):
        # need to include self.commitIdx, only up-to-date candidate could win
        election = messages.RequestVote(self.address, voter, term, self.lastLogIndex, self.lastLogTerm)
        while self.state == CANDIDATE and self.currentTerm == term:
            self.send_message(voter, election)

    # START PRESIDENT
    def start_heart_beat(self):
        print("Starting HEARTBEAT")
        for each in self.neighbors:
            t = threading.Thread(target=self.send_heartbeat, args=(each.address, ))
            t.start()

    def send_heartbeat(self, follower):
        message = messages.AppendEntry(
            self.address, follower, self.currentTerm, self.lastLogIndex, self.lastLogTerm, [], self.commitIdx)
        while self.state == LEADER:
            start = time.time()
            self.send_message(follower, message)
            delta = time.time() - start
            # keep the heartbeat constant even if the network speed is varying
            time.sleep((cfg.HB_TIME - delta) / 1000)

# Use zmq for the communication between servers.
class ZeroMQServer(Server):
    def __init__(self, address, neighbors, port = 8000):
        super(ZeroMQServer, self).__init__(address, neighbors)
        self.port = port

        class PublishThread(threading.Thread):
            def run(thread):
                context = zmq.Context()
                socket = context.socket(zmq.PUB)
                socket.bind("tcp://*:%d" % port)

                while True:
                    message = self.messageBoard.get_message()
                    if not message:
                        continue
                    messageStr = pickle.dumps(message)
                    socket.send_string(messageStr)

        class SubscribeThread(threading.Thread):
            def run(thread):
                context = zmq.Context()
                socket = context.socket(zmq.SUB)
                for neighbor in neighbors:
                    socket.connect("tcp://%s:%d" % (int(neighbor.address), int(neighbor.port)))

                while True:
                    messageStrByte = socket.recv_string()
                    message = pickle.loads(messageStrByte)
                    self.on_message(message)

        self.subscribeThread = SubscribeThread()
        self.publishThread = PublishThread()
        self.subscribeThread.daemon = True
        self.subscribeThread.start()
        self.publishThread.daemon = True
        self.publishThread.start()

if _name_ == "_main_":
    file_path = "../ips"
    servers = []
    with open(file_path, "r") as file:
        for line in file:
            neighbors = []
            for i in range(len(servers)):
                neighbors.append(servers[i])
            server = ZeroMQServer(line, neighbors)
            servers.append(server)
    #
    # majority = (len(servers) // 2) + 1
    #
    # for i in range(len(servers)):
    #     neighbors = []
    #     for j in range(len(servers)):
    #         if(i != j):
    #             neighbors.append(servers[i])
    #     servers[i].updateSubscribeThread(neighbors, majority)
    # #
    # # for server in servers:
    # #     neighbors = []
    # #     for i in range(len(servers)):
    # #         neighbors.append(servers[i])
    # #     server.updateSubscribeThread(majority)
