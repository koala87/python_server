# python_server

# router server, listen 58849, 3050, 25377, 11235 port
# based on tornado tcpserver
# run: ./route_server.py
route_server.py
    log.py
    config.py
    route.conf

# run: ./client.py
# packet header 24 bytes : author, version, request, length, verify, device
client.py
    packet.py
    
# java tcp server sample
java
    /TcpServer.java
    
# log dir
server
