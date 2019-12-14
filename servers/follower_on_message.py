from message import messages


# The message processing function for the follower
def follower_message(node, message):
    print("enter")
    if message.type == messages.AppendEntry:
        on_append_entries(node, message)
    elif message.type == messages.RequestVote:
        on_vote_request(node, message)
    elif message.type == messages.RequestVoteResponse:
        on_vote_received(node, message)
    elif message.type == messages.AppendEntryResponse:
        on_response_received(node, message)

# The message processing function for RequestVote message.
def on_vote_request(node, message):
    print("qwertyuio23456789")
    if node.last_vote is None and message.lastLogIndex >= node.lastLogIndex:
        node.send_vote_response_message(message)
    else:
        node.send_vote_response_message(message, yes=False)

    # return self, None

# The message processing function for AppendEntries message.
def on_append_entries(node, message):
    # heatbeat
    if (message.entries == {}):
        node.send_response_message(message)
        return

    # appendEntry
    log = node.log

    # 5
    # TODO: >
    if (message.leaderCommit != node.commitIndex):
        node.commitIndex = min(message.leaderCommit, len(log) - 1)

    # 2.1
    if (len(log) < message.prevLogIndex):
        node.send_response_message(message, yes=False)
        return

    # 2.2
    if (len(log) > 0 and
            log[message.prevLogIndex["term"]] != message.prevLogTerm):
        # TODO: ?
        # delete any entries in the follower's log after the agreed point
        node.log = log[:message.prevLogIndex]
        node.lastLogIndex = message.prevLogIndex
        node.lastLogTerm = message.prevLogTerm

        node.send_response_message(message, yes=False)
        return

    if (len(log) > 0 and message.leaderCommit > 0
            and log[message.leaderCommit]["term"] != message.term):
        # delete any entries in the follower's log after the agreed point
        log = log[:node.commitIndex]
        for entry in message.entries:
            log.append(entry)
            node.commitIndex += 1

        node.lastLogIndex = len(log) - 1
        node.lastLogTerm = log[-1]["term"]
        node.commitIndex = len(log) - 1
        node.log = log

        node.send_response_message(message)
        return

    if (len(message.entries) > 0):
        for entry in message.entries:
            node.log.append(entry)
            node.commitIndex += 1

        node.lastLogIndex = len(log) - 1
        node.lastLogTerm = log[-1]["term"]
        node.commitIndex = len(log) - 1
        node.log = log

        node.send_response_message(message)
        return

    node.send_response_message(message)

# The message processing function for RequestVote response message.
def on_vote_received(node, message):
    """This is called when this node recieves a vote."""


# The message processing function for AppendEntries response message.
def on_response_received(node, message):
    """This is called when a response is sent back to the Leader"""


# The message processing function for message from client.
def on_client_command(node, message):
    """This is called when there is a client request."""


# The function for sending vote response message.
def send_vote_response_message(node, msg, yes=True):
    print("fdjsakfheriughjklfa;")
    vote_response = messages.RequestVoteResponse(
        node.addresss,
        msg.sender,
        msg.term,
        yes)
    node.send_message_response(vote_response)

