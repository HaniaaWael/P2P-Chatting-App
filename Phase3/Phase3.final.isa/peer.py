import threading
from socket import *
import logging
import registry
import pickle
import rooms

exited = 0
# main process of the peer
class peerMain:

    # peer initializations
    def __init__(self):

        # ip address of the registry
        self.registryName = registry.return_ip()
        self.registryPort = 15000
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.connect((self.registryName, self.registryPort))

        # initializes udp socket which is used to send hello messages
        '''self.udpClientSocket = socket(AF_INET, SOCK_DGRAM)
        # udp port of the registry
        self.registryUDPPort = 15500'''
        # login info of the peer
        self.loginCredentials = (None, None)
        # online status of the peer
        self.udp_port=None
        self.isOnline = False
        # server port number of this peer
        self.peerServerPort = None
        # server of this peer
        self.peerServer = None
        # client of this peer
        self.peerClient = None
        # timer initialization
        self.timer = None


        choice = "0"
        # log file initialization
        logging.basicConfig(filename="peer.log", level=logging.INFO)
        # as long as the user is not logged out, asks to select an option in the menu


        logged_in=0
        global exited
        logged_in=exited
        while logged_in<1:
            choice = input("Please Choose an Option Out of The Following: \n1:Create New Account\n2:Login\n\n")


            if choice == "1":


                username = input("username: ")
                password = input("password: ")
                if len(username)<1 or len(password)<1:
                     x=0
                     while x < 1:

                         print("enter valid username or password")
                         username = input("username: ")
                         password = input("password: ")
                         if len(username)>0 and len(password)>0:
                             x=x+2
                         else:continue


                self.createAccount(username,password)


            # if choice is 2 and user is not logged in, asks for the username
            # and the password to login
            elif choice == "2" and not self.isOnline:
                username = input("username: ")
                password = input("password: ")

                if len(username)<1 or len(password)<1:
                     x=0
                     while x < 1:
                         print("enter valid username or password")
                         username = input("username: ")
                         password = input("password: ")
                         if len(username)>0 and len(password)>0:
                             x=x+2
                         else:continue


                # asks for the port number for server's tcp socket
                peerServerPort = int(input("Enter a port number for peer server: "))
                self.udp_port = int(input("Enter a udp port number for peer server: "))


                status = self.login(username, password, peerServerPort, self.udp_port)
                # is user logs in successfully, peer variables are set
                if status == 1:
                    self.isOnline = True
                    self.loginCredentials = (username, password)
                    self.peerServerPort = peerServerPort
                    logged_in=1

        choice1="0"
        while choice1 !="1":
                    # creates the server thread for this peer, and runs it
            choice1 = input("Please Choose an Option Out of The Following: \n1:Logout\n2:Search For an Online User\n3:Create New Chatroom\n4:List All Chatrooms\n5:Join a Chatroom\n\n")
            # if choice is 3 and user is logged in, then user is logged out
            # and peer variables are set, and server and client sockets are closed
            if choice1 == "1" and self.isOnline:
                self.logout(1)
                self.isOnline = False
                self.loginCredentials = (None, None)
                if self.peerClient is not None:
                    self.peerClient.tcpClientSocket.close()
                print("Logged out successfully")
            # is peer is not logged in and exits the program
            elif choice1 == "1":
                self.logout(2)
            # if choice is 2 and user is online, then user is asked
            # for a username that is wanted to be searched
            elif choice1 == "2" and self.isOnline:
                username = input("Username to be searched: ")
                searchStatus = self.searchUser(username)
                # if user is found its ip address is shown to user
                if searchStatus is not None and searchStatus != 0:
                    print("IP address of " + username + " is " + searchStatus)

            elif choice1 == "OK" and self.isOnline:
                okMessage = "OK " + self.loginCredentials[0]
                logging.info("Send to " + self.peerServer.connectedPeerIP + " -> " + okMessage)


            elif choice1 == "3":  # Create a new chatroom
                chatroom_name = input("Enter chatroom name: ")
                self.create_chatroom(chatroom_name)

            elif choice1 == "4":  # List all chatrooms
                self.list_chatrooms()

            elif choice1 == "5":  # Join a chatroom
                chatroom_id = input("Enter chatroom ID: ")
                self.join_chatroom(chatroom_id)







    # account creation function
    def createAccount(self, username, password):

        message = "JOIN " + username + " " + password
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "join-success":
            print("Account created...")
        elif response == "join-exist":
            print("choose another username or login...\n")
        '''elif response=="null_credentials":
            print("enter valid username and password")
            peerMain()'''



    # login function
    def login(self, username, password, peerServerPort ,udp_port):
        # a login message is composed and sent to registry
        # an integer is returned according to each response
        message = "LOGIN " + username + " " + password + " " +  str(peerServerPort) +" "+ str(udp_port)
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "login-success":
            self.username = username
            t1 = threading.Thread(target=self.udpServer, args=(self.udp_port,))
            t1.start()
            print("Logged in successfully...\n")
            return 1
        elif response == "login-account-not-exist":
            print("Account does not exist...\n")
            return 0

        elif response == "login-wrong-password":
            print("Wrong password...\n")
            return 3

    # logout function
    def logout(self, option):

        if option == 1:
            message = "LOGOUT " + self.loginCredentials[0]

        else:
            message = "LOGOUT"
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())

    # function for searching an online user
    def searchUser(self, username):

        message = "SEARCH " + username
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        logging.info("Received from " + self.registryName + " -> " + " ".join(response))
        if response[0] == "search-success":
            print(username + " is found successfully...\n")
            return response[1]
        elif response[0] == "search-user-not-online":
            print(username + " is not online...\n")
            return 0
        elif response[0] == "search-user-not-found":
            print(username + " is not found\n")
            return None

    def create_chatroom(self, chatroom_name):
        message = "CREATE_CHATROOM " + chatroom_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        if response == "create-chatroom-success":
            print("Chatroom created successfully.")
        else:
            print("Failed to create chatroom.")



    def join_chatroom(self, chatroom_id):
        message = "JOIN_CHATROOM " + str(chatroom_id)
        self.tcpClientSocket.send(message.encode())
        msg = self.tcpClientSocket.recv(1024)#how to for loop from this
        print(msg)
        details = pickle.loads(msg)

        response = self.tcpClientSocket.recv(1024).decode()
        if response == "join-chatroom-success":
            print("Joined chatroom successfully.")

            UDPClientSocket = socket(AF_INET, SOCK_DGRAM)

            rooms.room_users = details
            rooms.room_id = chatroom_id


            if isinstance(rooms.room_users, list) and rooms.room_users:
                rooms.room_users = [i for i in details if i != self.udp_port]


                for x in rooms.room_users:
                    try:
                        addresses = ("127.0.0.2", x)

                        msg_dict = {
                            "message": f"{self.username} has joined the chatroom",
                            "username": self.username,
                            "room_id": chatroom_id,
                            "udp_port": self.udp_port
                        }
                        UDPClientSocket.sendto(pickle.dumps(msg_dict), addresses)

                        #msg = "A new user joined the chat"
                        #UDPClientSocket.sendto(str.encode(msg), addresses)
                    except:
                        print("fail")
                        pass
            while True:
                my_msg = input( )
                if my_msg=="exit":
                    message = "EXIT_CHATROOM"
                    self.tcpClientSocket.send(message.encode())
                    response = self.tcpClientSocket.recv(1024).decode()
                    if response == "exit-chatroom-success":
                        print("Exited chatroom successfully.")
                        global exited
                        exited+=1
                        peerMain()



                        #close socket

                    else:
                        print("Failed to exit chatroom.")


                #print(details)
                # msg = pickle.loads(details)
                if isinstance(details, list) and details:
                    for x in rooms.room_users:
                        if x is not None:
                            try:
                                addresses = ("127.0.0.2", x)

                                msg_dict = {
                                    "message": f"{self.username}: {my_msg}",
                                    "username": self.username,
                                    "room_id": chatroom_id ,
                                    "udp_port": self.udp_port
                                }

                                UDPClientSocket.sendto(pickle.dumps(msg_dict), addresses)
                            except Exception as e:
                                print("Error sending message:", e)
        else:
            print("Failed to join chatroom.")

    def exit_chatroom(self):
        message = "EXIT_CHATROOM"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        if response == "exit-chatroom-success":
            print("Exited chatroom successfully.")
        else:
            print("Failed to exit chatroom.")

    def list_chatrooms(self):
        message = "LIST_CHATROOMS"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        print("Available chatrooms: " + response)

    def udpServer(self, udp_port):
         UDPServerSocket = socket(AF_INET, SOCK_DGRAM)
         addresses=("127.0.0.2",udp_port)
         UDPServerSocket.bind( addresses)
         print("UDP server up and listening")
         global exited
         if exited>0:
             UDPServerSocket.close()
         while(True):
            #msg = UDPServerSocket.recvfrom(1024)
            #message = msg[0]
            #address = msg[1]

            data, address = UDPServerSocket.recvfrom(1024)
            msg_dict = pickle.loads(data)

            message = msg_dict["message"]
            username = msg_dict["username"]
            room_id = msg_dict["room_id"]
            udp_port_clients = msg_dict["udp_port"]

            if(rooms.room_users.count(udp_port_clients)==0):
                rooms.room_users.append(udp_port_clients)
                print(rooms.room_users)

            if(rooms.room_id == room_id):
                clientMsg = format(message)
                print(clientMsg)  # Print the received message
                print()  # Print a new line for spacing
                #print(">> ", end='')







# peer is started
peerMain()
