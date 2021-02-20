import socket
import select


#initiating server socket
HEADER_LENGTH = 10
IP = socket.gethostname()  # 127.0.0.1 or other..
PORT = 1234
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creats socket, SOCK_STREAM=TCP
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # allow to reconnect

server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]  # connected sockets will be appended
clients = {}  # KEY= client_sockets, VALUTE= client_data


def recieve_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode("utf8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    '''
    the select module will listen on 3 things: read,write,exception iterables.
    the exceptions_sockets here are optional.
    mainly will be focus on the read sockets.
    * The first message will be the header+username of the client.
    '''
    for ready_socket in read_sockets:
        if ready_socket == server_socket:  # for the first run will wait for clients
            client_socket, client_addr = server_socket.accept()
            user = recieve_message(client_socket)
            if user is False:
                continue
            sockets_list.append(client_socket)
            clients[client_socket] = user
            print(f"Initiated connection with {client_addr}, username: {user['data'].decode('utf8')}")
        else:
            # Socket that already connected
            message = recieve_message(ready_socket)
            if message is False:  # if sent empty or lost connection
                print(f"Connection terminated with {clients[ready_socket]['data'].decode('utf8')}")
                sockets_list.remove(ready_socket)
                del clients[ready_socket]
                continue

            user = clients[ready_socket]
            print(f"Received message from {user['data'].decode('utf8')}: {message['data'].decode('utf8')}")

            for client_socket in clients:  # sending the message to all other clients
                if client_socket != ready_socket:  # except the sender..
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
        for ready_socket in exception_sockets:
            sockets_list.remove(ready_socket)
            del clients[ready_socket]
