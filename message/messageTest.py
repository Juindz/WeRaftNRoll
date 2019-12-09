from message import message
from message import messages
import unittest
from random import randint


class TestMessage(unittest.TestCase):

    def test_message(self):
        print("________test class Message_________ ")
        print("sender is 1, receiver is 2, term is 0, data is []")
        m = messages.Message(1, 2, 0, [])
        self.assertEqual(m.sender, 1)
        self.assertEqual(m.receiver, 2)
        self.assertEqual(m.term, 0)
        self.assertEqual(m.data, [])
        print("Testing Message setter")
        new_term = randint(0, 10)
        m.sender = new_term
        self.assertEqual(m.sender, new_term)

    def test_request_vote(self):
        print("_____________test request vote___________")
        print("sender = 5, receiver = 2, term = 0, data = []")
        m = messages.RequestVote(5, 2, 0, [])
        self.assertEqual(m.sender, 5)
        self.assertEqual(m.type, 3)

    def test_request_vote_response(self):
        print("_____________test request vote response___________")
        print("sender = 1, receiver = 1, term = 1, data = [1]")
        r = messages.RequestVoteResponse(1, 1, 1, [1])
        self.assertEqual(1, r.sender)
        self.assertEqual([1], r.data)
        self.assertEqual(r.type, 4)

    def test_append_entry(self):
        print("_____________test append entry___________")
        print("sender = 5, receiver = 2, term = 3, entries = [1,1,1,1], commitIndex = 5, prevLogIndex = 4, "
              "prevLogTerm = 2, data = []")
        r = messages.AppendEntry(5, 2, 3, [1, 1, 1, 1], 5, 4, 2, [])
        self.assertEqual(r.entries, [1, 1, 1, 1])
        self.assertEqual(r.prevLogIndex, 4)
        self.assertEqual(r.type, 1)

    def test_append_entry_response(self):
        print("_____________test append entry response___________")
        print("sender = 5, receiver = 2, term = 3, success = True, matchIndex = 3, data = []")
        r = messages.AppendEntryResponse(5, 2, 3, True, 3, [])
        self.assertTrue(r.success)
        self.assertEqual(r.matchIndex, 3)
