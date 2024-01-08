from locust import HttpUser, task, between

class PeerUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def create_account(self):
        self.client.post("/create_account", json={"username": "user1", "password": "password123"})
        self.client.post("/create_account", json={"username": "user2", "password": "password1234"})
        self.client.post("/create_account", json={"username": "user3", "password": "password12345"})
        self.client.post("/create_account", json={"username": "user4", "password": "password123456"})
        self.client.post("/create_account", json={"username": "user5", "password": "password1234567"})

    @task
    def login(self):
        self.client.post("/login", json={"username": "user1", "password": "password123", "peerServerPort": 12344, "udp_port": 15678})
        self.client.post("/login", json={"username": "user2", "password": "password1234", "peerServerPort": 123445,
                                         "udp_port": 25678})
        self.client.post("/login", json={"username": "user3", "password": "password12345", "peerServerPort": 1234456,
                                         "udp_port": 35678})
        self.client.post("/login", json={"username": "user4", "password": "password123456", "peerServerPort": 12344567,
                                         "udp_port": 45678})
        self.client.post("/login", json={"username": "user5", "password": "password1234567", "peerServerPort": 123445678,
                                         "udp_port": 55678})

    @task
    def logout(self):
        self.client.post("/logout", json={"option": 1})
        self.client.post("/logout", json={"option": 1})
        self.client.post("/logout", json={"option": 1})


    @task
    def search_user(self):
        self.client.post("/search_user", json={"username": "user1"})
        self.client.post("/search_user", json={"username": "user2"})
        self.client.post("/search_user", json={"username": "user2"})
        self.client.post("/search_user", json={"username": "user2"})
        self.client.post("/search_user", json={"username": "user1"})
        self.client.post("/search_user", json={"username": "user4"})
        self.client.post("/search_user", json={"username": "user5"})
        self.client.post("/search_user", json={"username": "user1"})

    @task
    def create_chatroom(self):
        self.client.post("/create_chatroom", json={"chatroom_name": "chatroom1"})
        self.client.post("/create_chatroom", json={"chatroom_name": "chatroom2"})
        self.client.post("/create_chatroom", json={"chatroom_name": "chatroom3"})
        self.client.post("/create_chatroom", json={"chatroom_name": "chatroom4"})


    @task
    def join_chatroom(self):
        self.client.post("/join_chatroom", json={"chatroom_id": 1})
        self.client.post("/join_chatroom", json={"chatroom_id": 2})
        self.client.post("/join_chatroom", json={"chatroom_id": 3})
        self.client.post("/join_chatroom", json={"chatroom_id": 4})
        self.client.post("/join_chatroom", json={"chatroom_id": 1})
        self.client.post("/join_chatroom", json={"chatroom_id": 2})
        self.client.post("/join_chatroom", json={"chatroom_id": 3})

    @task
    def exit_chatroom(self):
        self.client.post("/exit_chatroom")
        self.client.post("/exit_chatroom")
        self.client.post("/exit_chatroom")

    @task
    def list_chatrooms(self):
        self.client.get("/list_chatrooms")

    @task
    def udp_server(self):
        self.client.get("/udp_server")

