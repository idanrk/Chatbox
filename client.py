import socket
import errno
import sys

HEADER_LENGTH = 10
IP = socket.gethostname()
PORT = 1234
# initiating client socket
my_username = input("Enter username: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)
username = my_username.encode("utf8")
username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf8")  # len align to left with HL size spaces
client_socket.send(username_header + username)

while True:
    message = input("> ")

    if message:
        message = message.encode("utf8")
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf8")
        client_socket.send(message_header + message)
    try:
        # receives messages
        while True:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not username_header:
                print("Disconnected from server.. exiting..")
                sys.exit()
            '''
            the message from server pattern is:
            user-header+username + msg-header+message
            '''
            username_length = int(username_header.decode("utf8").strip())
            username = client_socket.recv(username_length).decode("utf8")

            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode("utf8").strip())
            message = client_socket.recv(message_length).decode("utf8")
            print(f"{username}> {message}")

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            # if its an error that's NOT 'no message received' then:
            print("Reading error", str(e))
            sys.exit()
        continue
    except Exception as e:
        print("Error occurred", str(e))
        sys.exit()
