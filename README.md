# WeRaftNRoll Python 3.7
A implementation of Raft using Python that handles the situation of Leader Flip-Flopping.
Information stored as pairs(variable_name, variable_value).

# How to run server
Currently, there are three servers, more servers can be added by making changes to 'ip_list.txt'.
One can initialize a server using its index in 'ip_list,=.txt'.
```
python3 server.py ip_list.txt 0
python3 server.py ip_list.txt 1
python3 server.py ip_list.txt 2
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
## Communication between client and server using zmq PUB/SUB and socket??

