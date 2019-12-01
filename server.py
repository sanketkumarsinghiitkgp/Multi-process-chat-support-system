import socket
import select
import time

HEADER_LENGTH = 10

replies={"time": time.ctime, "company name": "finhawk"}

def udreply(name,addr,query):
        if query == "my name":
            return name
        elif query == "my address":
            return addr
        else:
            return False
        
    
IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()

sockets_list = [server_socket]

clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

def sendformat(uname, body):
    username_header = f"{len(uname):<{HEADER_LENGTH}}".encode('utf-8')
    body_header = f"{len(body):<{HEADER_LENGTH}}".encode('utf-8')
    return username_header+uname.encode('utf-8')+body_header+body.encode('utf-8')

def receive_message(client_socket):

    try:

        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())

        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)


    for notified_socket in read_sockets:

        if notified_socket == server_socket:

            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)

            if user is False:
                continue

            sockets_list.append(client_socket)

            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        else:

            message = receive_message(notified_socket)

            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                sockets_list.remove(notified_socket)

                del clients[notified_socket]

                continue

            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            if message["data"].decode('utf-8') in replies:
                notified_socket.send(sendformat("Bot",replies[message["data"].decode('utf-8')]()))
            else:
                ret = udreply(user["data"].decode('utf-8'),clients[notified_socket]['data'].decode('utf-8'),message["data"].decode("utf-8"))
                if ret != False:
                    notified_socket.send(sendformat("Bot", ret))
                else:
                    rep = input("Bot cannot reply to this query, please enter reply.")
                    notified_socket.send(sendformat("Human Support",rep))

    for notified_socket in exception_sockets:

        sockets_list.remove(notified_socket)

        del clients[notified_socket]