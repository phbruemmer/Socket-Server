import socket
import time
import os
import encryption

host_name = socket.gethostname()
host = socket.gethostbyname(host_name)

server_ip = "172.31.6.223"

port = 6544

print(host_name)
print(host)
print(port)

buffer = 1024

s = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM,
    proto=0
)


def main():
    try:
        s.connect((server_ip, port))
        print(f"Successfully connected to the Server. ({server_ip}:{port})")
    except:
        print("Something went wrong.\nTry to contact the server host. (Probably the Server is not online.)")
        exit(-1)

    chat()


def file_uploader():
    print("# # # # # # #\nE N T E R - P A T H\n# # # # # # #\n")
    path = input("(path) > ")
    try:
        with open(path, 'rb') as file:
            s.send(encryption.encrypt_data('$upload', True).encode())
            time.sleep(.1)
            s.send(str(os.path.getsize(path)).encode())
            time.sleep(.1)
            s.send(os.path.basename(path).encode())
            file_chunk = file.read(1024)
            s.send(file_chunk)
            while file_chunk:
                print(file_chunk)
                file_chunk = file.read(1024)
                s.send(file_chunk)
                print(file_chunk)
                time.sleep(.1)
    except FileNotFoundError:
        print("# F I L E - N O T - F O U N D #")
    except Exception as err:
        print(err)


def chat():
    msg = input("> ")

    if msg == "$exit":
        msg = encryption.encrypt_data("$exit", True)
        s.send(msg.encode())
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        return

    if msg == "$upload":
        file_uploader()
    else:
        send(msg)
    chat()


def send(msg):
    msg = encryption.encrypt_data(msg, True)
    s.send(msg.encode())
    time.sleep(.1)
    recv()


def recv():
    msg = s.recv(buffer)
    msg = msg.decode()
    print(msg)
    msg = encryption.decrypt(msg)
    print(msg)


if __name__ == '__main__':
    main()
