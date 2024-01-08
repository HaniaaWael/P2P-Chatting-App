import hashlib
#takes the password from the user when they are signing up and hashes it and returns the hashed password
def hash_password (initial_password):
    h = hashlib.new("SHA256")
    h.update(initial_password.encode())
    password_hash = h.hexdigest()
    return password_hash

# hash compare takes the user input password when they are logging is and also take the hashed value from the database and compares them
def hash_compare (user_input,hashed):
    h = hashlib.new("SHA256")
    h.update(user_input.encode())
    input_hash = h.hexdigest()
    if (input_hash==hashed):
        return 1
    else: return 0