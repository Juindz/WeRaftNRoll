from message import messages
import unittest
from random import randint


class TestMessage(unittest.TestCase):

    def test_message(self):
        # def __init__(self, sender, receiver, term):
        print("________test class Message_________ ")
        print("sender is 1, receiver is 2, term is 0")
        m = messages.Message(1, 2, 0)
        self.assertEqual(m.sender, 1)
        self.assertEqual(m.receiver, 2)
        self.assertEqual(m.term, 0)
        print("Testing Message setter")
        new_term = randint(0, 10)
        m.sender = new_term
        self.assertEqual(m.sender, new_term)

    #    def __init__(self, sender, receiver, term, lastLogIndex, lastLogTerm):
    def test_request_vote(self):
        print("_____________test request vote___________")
        print("sender = 5, receiver = 2, term = 0, lastLogIndex = 3, lastLogTerm = 5")
        m = messages.RequestVote(5, 2, 0, 3, 5)
        self.assertEqual(m.sender, 5)
        self.assertEqual(m.lastLogIndex, 3)
        self.assertEqual(m.lastLogTerm, 5)
        self.assertEqual(m.type, 3)

    #  def __init__(self, sender, receiver, term, voteGranted):
    def test_request_vote_response(self):
        print("_____________test request vote response___________")
        print("sender = 1, receiver = 1, term = 1, voteGranted = True")
        r = messages.RequestVoteResponse(1, 1, 1, True)
        self.assertEqual(1, r.sender)
        self.assertTrue(r.voteGranted)
        self.assertEqual(r.type, 4)

    # def __init__(self, sender, receiver, term, prevLogIndex, prevLogTerm, entries, leaderCommit):
    def test_append_entry(self):
        print("_____________test append entry___________")
        print(
            "sender = 5, receiver = 2, term = 3, prevLogIndex = 3, prevLogTerm = 5, entries = [1,1,1,1], leaderCommit= 2  "
            "prevLogTerm = 2, data = []")
        r = messages.AppendEntry(5, 2, 3, 3, 5, [1, 1, 1, 1], 2)
        self.assertEqual(r.entries, [1, 1, 1, 1])
        self.assertEqual(r.prevLogIndex, 3)
        self.assertEqual(r.prevLogTerm, 5)
        self.assertEqual(r.leaderCommit, 2)
        self.assertEqual(r.type, 1)

    # def __init__(self, sender, receiver, term, success):
    def test_append_entry_response(self):
        print("_____________test append entry response___________")
        print("sender = 5, receiver = 2, term = 3, success = True")
        r = messages.AppendEntryResponse(5, 2, 3, True)
        self.assertTrue(r.success)
        self.assertEqual(r.term, 3)
