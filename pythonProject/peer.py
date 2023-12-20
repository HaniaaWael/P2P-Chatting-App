from socket import *
import logging
import registry


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

        while choice != "3":

            choice = input("Choose: \nCreate new account: 1\nLogin: 2\nLogout: 3\nSearch for an online user: 4\n\n")

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
                peerServerPort = 5000


                status = self.login(username, password, peerServerPort)
                # is user logs in successfully, peer variables are set
                if status == 1:
                    self.isOnline = True
                    self.loginCredentials = (username, password)
                    self.peerServerPort = peerServerPort
                    # creates the server thread for this peer, and runs it

            # if choice is 3 and user is logged in, then user is logged out
            # and peer variables are set, and server and client sockets are closed
            elif choice == "3" and self.isOnline:
                self.logout(1)
                self.isOnline = False
                self.loginCredentials = (None, None)
                if self.peerClient is not None:
                    self.peerClient.tcpClientSocket.close()
                print("Logged out successfully")
            # is peer is not logged in and exits the program
            elif choice == "3":
                self.logout(2)
            # if choice is 4 and user is online, then user is asked
            # for a username that is wanted to be searched
            elif choice == "4" and self.isOnline:
                username = input("Username to be searched: ")
                searchStatus = self.searchUser(username)
                # if user is found its ip address is shown to user
                if searchStatus is not None and searchStatus != 0:
                    print("IP address of " + username + " is " + searchStatus)

                    
                    
           

            elif choice == "OK" and self.isOnline:
                okMessage = "OK " + self.loginCredentials[0]
                logging.info("Send to " + self.peerServer.connectedPeerIP + " -> " + okMessage)





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
    def login(self, username, password, peerServerPort):
        # a login message is composed and sent to registry
        # an integer is returned according to each response
        message = "LOGIN " + username + " " + password + " " + str(peerServerPort)
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "login-success":
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


# peer is started
peerMain()



