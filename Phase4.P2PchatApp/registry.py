from socket import *
import threading
import select
import logging
import hash
import db
import pickle

# This class is used to process the peer messages sent to registry
# for each peer connected to registry, a new client thread is created
class ClientThread(threading.Thread):
    # initializations for client thread
    def __init__(self, ip, port, tcpClientSocket):
        threading.Thread.__init__(self)
        # ip of the connected peer
        self.ip = ip
        # port number of the connected peer
        self.port = port
        # socket of the peer
        self.tcpClientSocket = tcpClientSocket
        # username, online status
        self.username = None
        self.isOnline = True

        print("New thread started for " + ip + ":" + str(port))

    # main of the thread
    def run(self):
        # locks for thread which will be used for thread synchronization
        self.lock = threading.Lock()
        print("Connection from: " + self.ip + ":" + str(self.port))
        print("IP Connected: " + self.ip)

        while True:
            try:
                # waits for incoming messages from peers
                message = self.tcpClientSocket.recv(1024).decode().split()
                logging.info("Received from " + self.ip + ":" + str(self.port) + " -> " + " ".join(message))
                #   JOIN    #
                print(message,"xxxxxxxxxxx")
                if not message:
                    continue
                if message[0] == "JOIN":
                    # join-exist is sent to peer,
                    # if an account with this username already exists
                    '''if len(message[1]) or len(message[2] == 0):
                        response="null_credentials"'''
                    if db.is_username_taken(connection,message[1]):
                        response = "join-exist"
                        print("From-> " + self.ip + ":" + str(self.port) + " " + response)
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    # join-success is sent to peer,
                    # if an account with this username is not exist, and the account is created
                    else:
                        print("Received message:", message)
                        db.register(connection,message[1], hash.hash_password(message[2]))
                        response = "join-success"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                #   LOGIN    #
                elif message[0] == "LOGIN":

                    if db.get_password(connection,message[1]):
                        retrievedPass = db.get_password(connection,message[1])
                        if hash.hash_compare(message[2],retrievedPass):
                            self.username = message[1]
                            self.lock.acquire()
                            try:
                                tcpThreads[self.username] = self
                            finally:
                                self.lock.release()

                            db.login_peer(connection,message[1], self.ip, message[3],message[4])

                            response = "login-success"

                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.tcpClientSocket.send(response.encode())

                        # if password not matches and then login-wrong-password response is sent
                        else:
                            response = "login-wrong-password"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.tcpClientSocket.send(response.encode())



                    else:
                        response = "login-account-not-exist"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())


                elif message[0] == "LOGOUT":

                    if  message[1] is not None and db.is_peer_online(connection,message[1]):
                        db.logout_peer(connection, message[1])
                        self.lock.acquire()
                        response = "logout successful"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                        try:
                            if message[1] in tcpThreads:
                                del tcpThreads[message[1]]
                        finally:
                            self.lock.release()
                        print(self.ip + ":" + str(self.port) + " is logged out")
                        self.tcpClientSocket.close()

                        break
                    else:
                        self.tcpClientSocket.close()
                        break

                #   SEARCH  #
                elif message[0] == "SEARCH":
                    # checks if an account with the username exists
                    if db.is_username_taken(connection, message[1]):

                        if db.is_peer_online(connection,message[1]):
                            peer_info = db.get_peer_ip_port(connection,message[1])
                            response = "search-success " + str(peer_info[0]) + ":" + str(peer_info[1])
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.tcpClientSocket.send(response.encode())
                        else:
                            response = "search-user-not-online"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.tcpClientSocket.send(response.encode())
                    # enters if username does not exist
                    else:
                        response = "search-user-not-found"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())

                elif message[0] == "CREATE_CHATROOM":
                    chatroom_name = message[1]
                    db.create_new_chatroom(connection, chatroom_name)
                    response = "create-chatroom-success"
                    logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                    self.tcpClientSocket.send(response.encode())

                # Handle LIST_CHATROOMS message
                elif message[0] == "LIST_CHATROOMS":
                    chatrooms = db.get_all_chatrooms(connection)
                    response = "list-chatrooms " + str(chatrooms)
                    logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                    self.tcpClientSocket.send(response.encode())

                # Handle JOIN_CHATROOM message
                elif message[0] == "JOIN_CHATROOM":
                    chatroom_id = int(message[1])
                    details = db.room_details(connection,chatroom_id)##usernames,Ips,ports of the people in the room
                    msg = pickle.dumps(details)

                    self.tcpClientSocket.send(msg)
                    db.join_chatroom(connection, self.username, chatroom_id)
                    response = "join-chatroom-success"
                    logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                    self.tcpClientSocket.send(response.encode())

                # Handle EXIT_CHATROOM message
                elif message[0] == "EXIT_CHATROOM":

                    db.leave_chatroom(connection, self.username)
                    response = "exit-chatroom-success"
                    logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                    self.tcpClientSocket.send(response.encode())


            except OSError as oErr:
                logging.error("OSError: {0}".format(oErr))



hostname = gethostname()
try:
    host = gethostbyname(hostname)
except gaierror:
    import netifaces as ni
    host = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

def return_ip():
    return host

if __name__ == "__main__":

    # tcp port initializations
    print("Registy started...")
    port = 15000

    connection = db.connect()
    db.create_table(connection)
    db.create_chatrooms_table(connection)
    print("Registry IP address: " + host)
    print("Registry port number: " + str(port))



    # onlinePeers list for online account
    onlinePeers = {}
    # accounts list for accounts
    accounts = {}
    # tcpThreads list for online client's thread
    tcpThreads = {}

    tcpSocket = socket(AF_INET, SOCK_STREAM)

    tcpSocket.bind((host, port))

    tcpSocket.listen(5)

    # input sockets that are listened
    inputs = [tcpSocket]

    # log file initialization
    logging.basicConfig(filename="registry.log", level=logging.INFO)

    # as long as at least a socket exists to listen registry runs
    while inputs:

        print("Listening for incoming connections...")
        # monitors for the incoming connections
        readable, writable, exceptional = select.select(inputs, [], [])
        for s in readable:
            # if the message received comes to the tcp socket
            # the connection is accepted and a thread is created for it, and that thread is started
            if s is tcpSocket:
                tcpClientSocket, addr = tcpSocket.accept()
                newThread = ClientThread(addr[0], addr[1], tcpClientSocket)
                newThread.start()




    tcpSocket.close()

