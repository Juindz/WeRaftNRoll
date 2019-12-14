# WeRaftNRoll Python 3.7
A implementation of Raft using Python that handles the situation of Leader Flip-Flopping.
Information stored as pairs(variable_name, variable_value).

## How to run server
Users should add all of the IP addresses to the 'ips.txt', which to initial the servers. The default values of all the servers' ports are 8000.

```
python3 server.py
```

## How to run client
After initiationg all desired servers(which serve as leader, candidate and follower), client can perform two actions: insert information and retrive information. The command line takes in 3 parameters: server's ip, variable_name, variable_value(optional). 
Example inserting information: variable_name = x, variable_value = 1. 
```
python3 client.py http://127.0.0.1:5000 x 1
```
Example retrieving information: variable_name = x. 
```
python3 client.py http://127.0.0.1:5000 x
```
## Communication between client and server using zmq PUB/SUB socket
Our communication is based on zmq PUB/SUB methods.

### Subscribe Thread
We generate a socket for each server to listen all other servers. We regard all other severs have the different IP addresses, but same ports.
When a server receive a message, the server call the related function based on the message type, during which the server could generate response message and add it to its message board.

### Publish Thread
We generate a socket for each server, which connect to all other servers. If there are messages in the server's message board, the server use the socket to send these messages to all other servers. 
