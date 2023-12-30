# 1.create db                                                                                //done
# 2.check if username exists before to ask for another username for signup                   //done
# 3.signup(register)                                                                          //done
# 4.get password (retrieves the password for a given username) for login checking credentials //done
# 5.if account is online (checks if account with certain username is online)                    //done
# 6.get list of who are currently online                                                            //done
# 7.Login when username and password confirmed get the user's ip and port no. and save them in db ...   //done
# and set this user as online                                                                           //done
# 8.Logout will set this user as offline                                                                //done
# 9.retrieve ip address and port number of an online user                                               //done

# Adding all queries outside code makes them easier to use :
# DATABASE QUERIES
import sqlite3

CREATE_PEERS_TABLE = """
CREATE TABLE IF NOT EXISTS peers (
    username TEXT PRIMARY KEY,
    password Varchar(100),  
    ip_address VARCHAR(15),  
    port_number INTEGER,
    udp_port INTEGER,

    is_online BOOLEAN,
    chatroom_id INTEGER
);
"""

# adding data to the table using users input //for signup //register
INSERT_NEW_PEER = "INSERT INTO peers (username, password) VALUES (?, ?);"

# checking if username is used by another user
CHECK_USERNAME_EXISTENCE = "SELECT EXISTS(SELECT 1 FROM peers WHERE username = ?);"

# for checking credentials for login
GET_PASSWORD = "SELECT password FROM peers WHERE username = ?;"

LOGIN_PEER = "UPDATE peers SET ip_address = ?, port_number = ?, udp_port=?, is_online = 1 WHERE username = ?;"

IS_PEER_ONLINE = "SELECT is_online FROM peers WHERE username = ?;"

GET_ONLINE_USERS = "SELECT username FROM peers WHERE is_online = 1;"

LOGOUT_PEER = "UPDATE peers SET is_online = 0 WHERE username = ?;"

GET_PEER_IP_PORT = "SELECT ip_address, port_number FROM peers WHERE username = ?;"
GET_PEER_PORTS = "SELECT udp_port FROM peers WHERE chatroom_id = ?;"


# FUNCTIONS OF INTERACTION WITH DATABASE

def connect():
    # 1 create our database by adding a data file
    return sqlite3.connect("data.db", check_same_thread=False)


# execute queries to create a table
# note:"with connection" ensure that when we execute our query to create the db table it actually gets saved to the file

# whoever calls create table have to give it parameter "connection" that it has to use in order to execute queries
def create_table(connection):
    with connection:
        connection.execute(CREATE_PEERS_TABLE)


def register(connection, username, password):
    with connection:
        connection.execute(INSERT_NEW_PEER, (username, password))


def is_username_taken(connection, username):
    with connection:
        result = connection.execute(CHECK_USERNAME_EXISTENCE, (username,)).fetchone()
        return bool(result[0])


# if record itself not found it will return false, so we'll say that account does not exist
# if found and password is returned , we compare this password with password the user is provided while logging in

def get_password(connection, username):
    with connection:
        result = connection.execute(GET_PASSWORD, (username,)).fetchone()
        return result[0] if result else False


def login_peer(connection, username, ip_address, port_number, udp_port):
    with connection:
        connection.execute(LOGIN_PEER, (ip_address, port_number, udp_port, username))


# this function will return 3 cases :
# true if user is online / false if user offline / "not found" if username we search for is not found in db
def is_peer_online(connection, username):
    with connection:
        result = connection.execute(IS_PEER_ONLINE, (username,)).fetchone()
        if result is not None:
            return True if result[0] else False  # this means it found username, return online or not
        else:
            return "Not Found"  # will say that username was not found


# this function will list usernames of current online users
def get_online_users(connection):
    with connection:
        result = connection.execute(GET_ONLINE_USERS).fetchall()
        return [row[0] for row in result]


# make peer offline
def logout_peer(connection, username):
    with connection:
        connection.execute(LOGOUT_PEER, (username,))


# return ip and port if a certain user if not found returns none
def get_peer_ip_port(connection, username):
    with connection:
        result = connection.execute(GET_PEER_IP_PORT, (username,)).fetchone()
        return result if result else (None, None)


# def room_details(connection, chatroom_id):
#     with connection:
#         results = connection.execute(GET_PEER_PORTS, (chatroom_id,)).fetchall()
#         if results:
#             # Extracting udp_port from each row in results
#             return [row[0] for row in results]
#         else:
#             # Return an appropriate message or an empty list if no users are found in the chatroom
#             return 0  # or return []

def room_details(connection, chatroom_id):
    with connection:
        results = connection.execute(GET_PEER_PORTS, (chatroom_id,)).fetchall()
        if results:
            return [row[0] for row in results]
        else:
            return []

'''def room_details(connection,chatroom_id):
    with connection:
        return connection.execute(GET_PEER_PORTS,(chatroom_id,))'''

# table for chatrooms
# 1.create table chatrooms
# 2.create new chatroom
# 3.join existing chatroom
# 4. exit chatroom
# 5. return list of chatrooms


CREATE_CHATROOMS_TABLE = """
CREATE TABLE IF NOT EXISTS chatrooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);
"""

JOIN_CHATROOM = "UPDATE peers SET chatroom_id = ? WHERE username = ?;"
LEAVE_CHATROOM = "UPDATE peers SET chatroom_id = NULL WHERE username = ?;"

# To create a new chatroom
INSERT_NEW_CHATROOM = "INSERT INTO chatrooms (name) VALUES (?);"

# To list all chatrooms
GET_ALL_CHATROOMS = "SELECT * FROM chatrooms;"

# To list users in a specific chatroom
GET_USERS_IN_CHATROOM = "SELECT username FROM peers WHERE chatroom_id = ?;"


def create_chatrooms_table(connection):
    with connection:
        connection.execute(CREATE_CHATROOMS_TABLE)


def create_new_chatroom(connection, name):
    with connection:
        connection.execute(INSERT_NEW_CHATROOM, (name,))


def join_chatroom(connection, username, chatroom_id):
    with connection:
        connection.execute(JOIN_CHATROOM, (chatroom_id, username))
        return


def leave_chatroom(connection, username):
    with connection:
        connection.execute(LEAVE_CHATROOM, (username,))


def get_all_chatrooms(connection):
    with connection:
        return connection.execute(GET_ALL_CHATROOMS).fetchall()


def get_users_in_chatroom(connection, chatroom_id):
    with connection:
        return connection.execute(GET_USERS_IN_CHATROOM, (chatroom_id,)).fetchall()


def delete_chatroom(connection, chatroom_id):
    # First, remove all users from this chatroom.
    with connection:
        connection.execute("UPDATE peers SET chatroom_id = NULL WHERE chatroom_id = ?;", (chatroom_id,))

    # Then, delete the chatroom itself.
    with connection:
        connection.execute("DELETE FROM chatrooms WHERE id = ?;", (chatroom_id,))


