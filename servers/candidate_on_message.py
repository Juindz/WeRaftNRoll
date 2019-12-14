from message import messages


# The message processing function for the candidate
def candidate_message(self, message):
    """This method is called when a message is received,
    and calls one of the other corrosponding methods
    that this state reacts to.

    """
    _type = message.type

    if _type == messages.AppendEntry:
        self.on_append_entries(message)
    elif _type == messages.RequestVote:
        self.on_vote_request(message)
    elif _type == messages.RequestVoteResponse:
        self.on_vote_received(message)
    elif _type == messages.AppendEntryResponse:
        self.on_response_received(message)


# The message processing function for RequestVote message.
def on_vote_request(self, message):
    if message.sender == self.address:
        self.send_vote_response_message(message)
    else:
        self.send_vote_response_message(message, yes=False)


# The message processing function for RequestVote response message.
def on_vote_received(self, message):
    print(self.address + " " + "on_vote_received")
    if message.sender not in self.votes and message.voteGranted:
        # print(f"RECEIVED VOTE from {message.sender}")
        self.votes[message.sender] = message
        self.increment_vote()
    elif message.term > self.currentTerm:
        # they declined because either I'm out-of-date or not newest term
        # update my term and change the state to FOLLOWER
        self.currentTerm = message.term
        self.vote = []
        self.voteCount = 0
        self.state = self.FOLLOWER


# The message processing function for AppendEntries message.
def on_append_entries(self, message):
    """This is called when there is a request to
    append an entry to the log.
    """
    if message.term > self.currentTerm:
        self.currentTerm = message.term
        self.vote = []
        self.voteCount = 0
        self.state = self.FOLLOWER
    else:
        self.send_response_message(message, yes=False)

# The message processing function for AppendEntries response message.
def on_response_received(self, message):
    """This is called when a response is sent back to the Leader"""

# The message processing function for message from client.
def on_client_command(self, message):
    """This is called when there is a client request."""

# sender, receiver, term, voteGranted
# The function for sending vote response message.
def send_vote_response_message(self, msg, yes=True):
    vote_response = messages.RequestVoteResponse(
        self.addresss,
        msg.sender,
        msg.term,
        yes)
    self.send_message_response(vote_response)

