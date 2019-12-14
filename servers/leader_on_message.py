from message import messages


# The message processing function for the leader
def leader_message(self, message):
    if message.type == messages.AppendEntry:
        self.on_append_entries(message)
    elif message.type == message.RequestVote:
        self.on_vote_request(message)
    elif message.type == messages.RequestVoteResponse:
        self.on_vote_received(message)
    elif message.type == message.AppendEntryResponse:
        self.on_response_received(message)


# The message processing function for AppendEntries response message.
def on_response_received(self, message):
    if message.term > self.currentTerm:
        self.currentTerm = message.term
        self.state = self.FOLLOWER
        self.init_timeout()
    
    # Was the last AppendEntries good?
    if not message.success():
        # No, so lets back up the log for this node
        self.nextIndexes[message.sender] -= 1

        # Get the next log entry to send to the client.
        previous_index = max(0, self.nextIndexes[message.sender] - 1)
        next_index = self.nextIndexes[message.sender]

        # Send the new log to the client and wait for it to respond.
        appendEntry = messages.AppendEntry(
            self.address, message.sender, self.term, previous_index, self.log[previous_index]["term"], 
            [self.log[next_index]], self.commitIndex)

        self.send_response_message(appendEntry)
    else:
        # commit check
        # TODO: tempName -> new name
        # matchIndex
        logIndex = self._nextIndexes[message.sender]
        self.logYesCountDict[logIndex] += 1
        if (self.logYesCountDict[logIndex] >= self.majority):
            self.commit_table[self.commitIndex] = self.log[logIndex]
            self.commitIndex += 1
        # update matchIndex
        self._matchIndex[message.sender] = self._nextIndexes[message.sender]

        # The last append was good so increase their index.
        self._nextIndexes[message.sender] += 1

        # Are they caught up?
        if self._nextIndexes[message.sender] > self.lastLogIndex:
            self._nextIndexes[message.sender] = self.lastLogIndex


# The message processing function for RequestVote message.
def on_vote_request(self, message):
    """This is called when there is a vote request."""


# The message processing function for RequestVote response message.
def on_vote_received(self, message):
    """This is called when this node recieves a vote."""


# The message processing function for AppendEntries message.
def on_append_entries(self, message):
    """This is called when there is a request to
    append an entry to the log.

    """


# The message processing function for message from client.
def on_client_command(self, message):
    """This is called when there is a client request."""
