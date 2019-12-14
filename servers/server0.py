import flask
import sys
from .servers import raftNode
# initialized 
if __name__ == '__main__':
    print( "python3 server.py <index> <txtfile>")
    web = flask.Flask(__name__)
    # python file, txt file, index
    python_file = sys.argv[0]
    txt_file = sys.argv[1]
    index = sys.argv[2]
    ips = []
    with open(txt_file) as f:
        for ip in f:
            ips.append(ip.strip())
    des_ip = ips.pop(index)
    # initialize server with ip and port
    info = des_ip.split(':')
    port = info[2]
    s = raftNode(ips, des_ip)
    web.run(host="0.0.0.0", port=int(port))
