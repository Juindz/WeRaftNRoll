import time
import socket
import logging


class Message(object):
    # correspond to type 
    AppendEntry = 1
    AppendEntryResponse = 2
    RequestVote = 3
    RequestVoteResponse = 4

    # underscore before variable to define private variable
    # message sent by a sender (its port number )and to a reciever(its port number), has its own term
    def __init__(self, sender, receiver, term):
        self._sender = sender
        self._receiver = receiver
        self._term = term
        time_record = time.time()
        self._timeStamp = int(time_record)

    @property
    def receiver(self):
        return self._receiver

    @property
    def sender(self):
        return self._sender

    @property
    def timestamp(self):
        return self._timeStamp

    @property
    def term(self):
        return self._term

    @term.setter
    def term(self, value):
        self._term = value

    @receiver.setter
    def receiver(self, value):
        self._receiver = value

    @sender.setter
    def sender(self, value):
        self._sender = value


class RequestVote(Message):

    def __init__(self, sender, receiver, term, lastLogIndex, lastLogTerm):
        Message.__init__(self, sender, receiver, term)
        self._lastLogIndex = lastLogIndex
        self._lastLogTerm = lastLogTerm
        self._type = Message.RequestVote

    @property
    def type(self):
        return self._type

    @property
    def lastLogTerm(self):
        return self._lastLogTerm

    @property
    def lastLogIndex(self):
        return self._lastLogIndex

class RequestVoteResponse(Message):

    def __init__(self, sender, receiver, term, voteGranted):
        Message.__init__(self, sender, receiver, term)
        self._type = Message.RequestVoteResponse
        self._voteGranted = voteGranted

    @property
    def type(self):
        return self._type
    
    @property
    def voteGranted(self):
        return self._voteGranted



class AppendEntry(Message):

    def __init__(self, sender, receiver, term, prevLogIndex, prevLogTerm, entries, leaderCommit):
        Message.__init__(self, sender, receiver, term)
        self._type = Message.AppendEntry
        self._entries = entries
        self._leaderCommit = leaderCommit
        self._prevLogTerm = prevLogTerm
        self._prevLogIndex = prevLogIndex

    @property
    def type(self):
        return self._type

    @property
    def entries(self):
        return self._entries

    @property
    def leaderCommit(self):
        return self._leaderCommit

    @property
    def prevLogTerm(self):
        return self._prevLogTerm

    @property
    def prevLogIndex(self):
        return self._prevLogIndex


class AppendEntryResponse(Message):
    # success = True if pass prevelogindex and prevlogterm checks
    # term = current term
    def __init__(self, sender, receiver, term, success):
        Message.__init__(self, sender, receiver, term)
        self._success = success
        self._type = Message.AppendEntryResponse

    @property
    def type(self):
        return self._type

    @property
    def success(self):
        return self._success



