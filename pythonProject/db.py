

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
    is_online BOOLEAN
);
"""

# adding data to the table using users input //for signup //register
INSERT_NEW_PEER = "INSERT INTO peers (username, password) VALUES (?, ?);"

# checking if username is used by another user
CHECK_USERNAME_EXISTENCE = "SELECT EXISTS(SELECT 1 FROM peers WHERE username = ?);"

# for checking credentials for login
GET_PASSWORD = "SELECT password FROM peers WHERE username = ?;"

LOGIN_PEER = "UPDATE peers SET ip_address = ?, port_number = ?, is_online = 1 WHERE username = ?;"

IS_PEER_ONLINE = "SELECT is_online FROM peers WHERE username = ?;"

GET_ONLINE_USERS = "SELECT username FROM peers WHERE is_online = 1;"

LOGOUT_PEER = "UPDATE peers SET is_online = 0 WHERE username = ?;"

GET_PEER_IP_PORT = "SELECT ip_address, port_number FROM peers WHERE username = ?;"


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


def login_peer(connection, username, ip_address, port_number):
    with connection:
        connection.execute(LOGIN_PEER, (ip_address, port_number, username))


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


