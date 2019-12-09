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
    def __init__(self, sender, receiver, term, data):
        self._sender = sender
        self._receiver = receiver
        self._term = term
        self._data = data
        time_record = time.time()
        self._timeStamp = int(time_record)

    @property
    def receiver(self):
        return self._receiver

    @property
    def sender(self):
        return self._sender

    @property
    def data(self):
        return self._data

    @property
    def timestamp(self):
        return self._timeStamp

    @property
    def term(self):
        return self._term

    @data.setter
    def data(self, value):
        self._data = value

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

    def __init__(self, sender, receiver, term, data):
        Message.__init__(self, sender, receiver, term, data)
        self._type = Message.RequestVote

    @property
    def type(self):
        return self._type


class RequestVoteResponse(Message):

    def __init__(self, sender, receiver, term, data):
        Message.__init__(self, sender, receiver, term, data)
        self._type = Message.RequestVoteResponse

    @property
    def type(self):
        return self._type


class AppendEntry(Message):

    def __init__(self, sender, receiver, term, entries, commitIndex, prevLogIndex, prevLogTerm, data):
        Message.__init__(self, sender, receiver, term, data)
        self._type = Message.AppendEntry
        self._entries = entries
        self._commitIndex = commitIndex
        self._prevLogTerm = prevLogTerm
        self._prevLogIndex = prevLogIndex

    @property
    def type(self):
        return self._type

    @property
    def entries(self):
        return self._entries

    @property
    def commitIndex(self):
        return self._commitIndex

    @property
    def prevLogTerm(self):
        return self._prevLogTerm

    @property
    def prevLogIndex(self):
        return self._prevLogIndex


class AppendEntryResponse(Message):

    def __init__(self, sender, receiver, term, success, matchIndex, data):
        Message.__init__(self, sender, receiver, term, data)
        self._success = success
        self._type = Message.AppendEntryResponse
        self._matchIndex = matchIndex

    @property
    def type(self):
        return self._type

    @property
    def success(self):
        return self._success


    @property
    def matchIndex(self):
        return self._matchIndex



