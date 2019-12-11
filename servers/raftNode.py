import threading
import time
from config import cfg

FOLLOWER = 0
CANDIDATE = 1
LEADER = 2


class Node():
    def __init__(self, fellow, my_ip):
        self.addr = my_ip
        self.fellow = fellow
        self.lock = threading.Lock()
        self.DB = {}
        self.log = []
        self.staged = None
        self.term = 0
        self.status = FOLLOWER
        self.majority = ((len(self.fellow) + 1) // 2) + 1
        self.voteCount = 0
        self.commitIdx = 0
        self.timeout_thread = None

        self.init_startElection_timeout()

    # increment only when we are candidate and receive positve vote
    # change status to LEADER and start heartbeat as soon as we reach majority
    def incrementVote(self):
        self.voteCount += 1
        if self.voteCount >= self.majority:
            print(f"{self.addr} becomes the leader of term {self.term}")
            self.status = LEADER
            self.startHeartBeat()

    # vote for myself, increase term, change status to candidate
    # reset the timeout and start sending request to followers
    def startElection(self):
        self.term += 1
        self.voteCount = 0
        self.status = CANDIDATE

        self.init_startElection_timeout()
        self.incrementVote()
        self.send_vote_req()

    # ------------------------------
    # ELECTION TIME CANDIDATE

    # spawn threads to request vote for all followers until get reply
    def send_vote_req(self):
        # TODO: use map later for better performance
        # we continue to ask to vote to the address that haven't voted yet
        # till everyone has voted
        # or I am the leader
        for voter in self.fellow:
            threading.Thread(target=self.ask_for_vote,
                             args=(voter, self.term)).start()

    # request vote to other servers during given election term
    def ask_for_vote(self, voter, term):
        # need to include self.commitIdx, only up-to-date candidate could win
        message = {
            "term": term,
            "commitIdx": self.commitIdx,
            "staged": self.staged
        }
        route = "vote_req"
        while self.status == CANDIDATE and self.term == term:
            reply = utils.send(voter, route, message)
            if reply:
                choice = reply.json()["choice"]
                # print(f"RECEIVED VOTE {choice} from {voter}")
                if choice and self.status == CANDIDATE:
                    self.incrementVote()
                elif not choice:
                    # they declined because either I'm out-of-date or not newest term
                    # update my term and terminate the vote_req
                    term = reply.json()["term"]
                    if term > self.term:
                        self.term = term
                        self.status = FOLLOWER
                    # fix out-of-date needed
                break

    # ------------------------------
    # ELECTION TIME FOLLOWER

    # some other server is asking
    def decide_vote(self, term, commitIdx, staged):
        # new election
        # decline all non-up-to-date candidate's vote request as well
        # but update term all the time, not reset timeout during decision
        # also vote for someone that has our staged version or a more updated one
        if self.term < term and self.commitIdx <= commitIdx and (
                staged or (self.staged == staged)):
            self.reset_timeout()
            self.term = term
            return True, self.term
        else:
            return False, self.term

    # ------------------------------
    # START PRESIDENT
    # TODO: leader part-

    def startHeartBeat(self):
        print("Starting HEARTBEAT")
        # TODO: Why ? empty entries for heartbeat
        if self.staged:
            # we have something staged at the beginngin of our leadership
            # we consider it as a new payload just received and spread it arount
            self.handle_put(self.staged)

        for each in self.fellow:
            t = threading.Thread(target=self.send_heartbeat, args=(each, ))
            t.start()

    def update_follower_commitIdx(self, follower):
        route = "heartbeat"
        first_message = {"term": self.term, "addr": self.addr}
        second_message = {
            "term": self.term,
            "addr": self.addr,
            "action": "commit",
            "payload": self.log[-1]
        }
        reply = utils.send(follower, route, first_message)
        if reply and reply.json()["commitIdx"] < self.commitIdx:
            # they are behind one commit, send follower the commit:
            reply = utils.send(follower, route, second_message)

    def send_heartbeat(self, follower):
        # check if the new follower have same commit index, else we tell them to update to our log level
        if self.log:
            self.update_follower_commitIdx(follower)

        route = "heartbeat"
        message = {"term": self.term, "addr": self.addr}
        while self.status == LEADER:
            start = time.time()
            reply = utils.send(follower, route, message)
            if reply:
                self.heartbeat_reply_handler(reply.json()["term"],
                                             reply.json()["commitIdx"])
            delta = time.time() - start
            # keep the heartbeat constant even if the network speed is varying
            time.sleep((cfg.HB_TIME - delta) / 1000)

    # we may step down when get replied
    def heartbeat_reply_handler(self, term, commitIdx):
        # i thought i was leader, but a follower told me
        # that there is a new term, so i now step down
        if term > self.term:
            self.term = term
            self.status = FOLLOWER
            self.init_startElection_timeout()

        # TODO logging replies

    # ------------------------------
    # FOLLOWER STUFF

    # TODO: change random_timout function
    # Timeout for RequestVote
    def reset_timeout(self, timeout = 150):
        # paper: election timeouts are chosen randomly from a fixed interval(e.g., 150–300 ms).
        self.election_time = time.time() + + random.randrange(timeout, 2 * timeout)

    # Heartbeat Receiver Function
    def heartbeat_follower(self, message):
        # TODO: why the weird case
        # weird case if 2 are PRESIDENT of same term. both receive an heartbeat. we will both step down
        # TODO: <= or <
        if self.term <= message["term"]:
            self.leader = message["addr"]
            self.reset_timeout()

            # lost in election
            if self.status == CANDIDATE:
                self.status = FOLLOWER
            elif self.status == LEADER:
                self.status = FOLLOWER
                self.init_startElection_timeout()

            # i have missed a few messages
            if self.term < message["term"]:
                self.term = message["term"]

            # TODO: Why handle client request ? It should be in AppendEntries
            if "action" in message:
                print("received action", message)
                # logging after first message
                if message["action"] == "log":
                    self.staged = message["payload"]
                # proceeding staged transaction
                elif self.commitIdx <= message["commitIdx"]:
                    if not self.staged:
                        self.staged = message["payload"]
                    # TODO: why commit? It should be in leader function
                    self.commit()

        return self.term, self.commitIdx

    def init_startElection_timeout(self):
        # thread function, stop when winning election
        self.reset_timeout()
        # initiate timeout thread
        if not self.timeout_thread or not self.timeout_thread.isAlive():
            self.timeout_thread = threading.Thread(target=self.timeout_thread)
            self.timeout_thread.start()

    def timeout_thread(self):
        while self.status != LEADER:
            dtime = self.election_time - time.time()
            if dtime < 0:
                self.startElection()
            else:
                time.sleep(dtime)

    # TODO: handle_get -> get_value_from_DB, remenber update function name
    def get_value_from_DB(self, dict):
        print("getting", dict)
        key = dict["key"]
        if key in self.DB:
            dict["value"] = self.DB[key]
            return dict
        else:
            return None

    # leader handle request, AppendEntries? log entries to store (empty for heartbeat)
    def handle_put(self, entries):
        self.lock.acquire()

        self.staged = entries
        log_message = {
            "term": self.term,
            "addr": self.addr,
            "payload": entries,
            "action": "log",
            "commitIdx": self.commitIdx
        }

        # spread log to everyone
        replay_confirmations = []
        for i in len(self.fellow):
            replay_confirmations.append(False)
        threading.Thread(target=self.spread_message, args=(log_message, replay_confirmations)).start()

        waited = 0
        while sum(log_confirmations) + 1 < self.majority:
            waited += 0.0005
            time.sleep(0.0005)
            if waited > cfg.MAX_LOG_WAIT / 1000:
                print(f"waited {cfg.MAX_LOG_WAIT} ms, update rejected:")
                self.lock.release()
                return False

        # reach this point only if a majority has replied and tell everyone to commit
        commit_message = {
            "term": self.term,
            "addr": self.addr,
            "payload": entries,
            "action": "commit",
            "commitIdx": self.commitIdx
        }
        self.commit()
        # TODO: why use thread ?
        threading.Thread(target=self.spread_commit_message, args=(commit_message, self.lock)).start()
        print("majority reached, replied to client, sending message to commit")
        return True

    # TODO: why heartbeat if value_put() call this function ?
    # TODO: it should be AppendEntries
    def spread_message(self, message, replay_confirmations):
        for i, each in enumerate(self.fellow):
            if utils.send(each, "heartbeat", message):
                # print(f" - - {message['action']} by {each}")
                replay_confirmations[i] = True
    # TODO: why heartbeat if value_put() call this function ?
    def spread_commit_message(self, message, lock):
        for i, each in enumerate(self.fellow):
            utils.send(each, "heartbeat", message)
        lock.release()

    def commit(self):
        self.commitIdx += 1
        self.log.append(self.staged)
        self.DB[self.staged["key"]] = self.staged["value"]
        self.staged = None
