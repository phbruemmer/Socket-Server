import os
import socket
import struct
import time

import encryption

HOST_NAME = socket.gethostname()
# HOST = socket.gethostbyname(HOST_NAME)
HOST = "127.0.0.1"
PORT = 6544

BUFFER = 64000

print(HOST_NAME)
print(HOST)
print(PORT)

s = socket.socket(socket.AF_INET,
                  socket.SOCK_STREAM)


def main():
    try:
        s.bind((HOST, PORT))
        print("Starting...")
    except Exception as err:
        print(err)
        exit(-1)

    s.listen(1)

    def accept():
        client_sock, client_addr = s.accept()
        loop(client_sock)

    def loop(client_sock):
        def handle_upload():
            upload_dir = "./uploaded_files/"

            def check_path(f):
                print("Checking path...")
                path_free = True
                if os.path.exists(os.path.join(upload_dir, f)):
                    path_free = False
                client_sock.sendall(struct.pack('?', path_free))
                return path_free

            def rename_response():
                response = struct.unpack('?', client_sock.recv(1))[0]
                print(response)                                                                             # Debugging
                return response

            def rename_sequence():
                """
                - request new name...
                - check availability
                    (if available return True / if not available return False)
                :return:
                """
                new_filename = client_sock.recv(BUFFER).decode()
                while not check_path(new_filename):
                    new_filename = client_sock.recv(BUFFER).decode()

            filename = client_sock.recv(BUFFER).decode()

            path_available = check_path(filename)

            if not path_available:
                ask_rename_response = rename_response()
                if not ask_rename_response:
                    return
                else:
                    rename_sequence()

            filename = client_sock.recv(BUFFER).decode()
            print(filename)

            with open(os.path.join(upload_dir, filename), 'wb') as file:
                _data = client_sock.recv(BUFFER)
                while not _data == b"$upload-finished":
                    print(_data.decode())
                    file.write(_data)
                    _data = client_sock.recv(BUFFER)
                    time.sleep(.1)

        def handle_download():
            uploaded_files = "./uploaded_files/"
            filename = client_sock.recv(BUFFER).decode()
            file_path = uploaded_files + filename
            time.sleep(.1)
            if os.path.exists(file_path):
                client_sock.sendall(str(os.path.getsize(file_path)).encode())
            else:
                client_sock.sendall("0".encode())
                return
            time.sleep(.1)
            with open(file_path, "rb") as file:
                file_chunk = file.read(1024)
                print(file_chunk.decode())
                client_sock.sendall(file_chunk)
                while not file_chunk.decode() == "":
                    print(file_chunk)
                    file_chunk = file.read(1024)
                    client_sock.sendall(file_chunk)
                    time.sleep(.1)
                client_sock.sendall("$download-finished".encode())

        def dirs():
            uploaded_files = './uploaded_files/'
            print(os.listdir(uploaded_files))
            for i in os.listdir(uploaded_files):
                client_sock.sendall(i.encode())
                time.sleep(.1)
            client_sock.sendall(b'$end-li')

        def helper():
            pass

        data = client_sock.recv(BUFFER)
        data = data.decode()
        decrypted_data = encryption.decrypt(data)
        print(decrypted_data)

        if decrypted_data == '$upload':
            handle_upload()
        elif decrypted_data == "$download":
            handle_download()
        elif decrypted_data == "$dirs":
            dirs()
        elif decrypted_data == "$help":
            helper()
        elif decrypted_data == "$exit":
            client_sock.shutdown(socket.SHUT_RDWR)
            client_sock.close()
            return
        else:
            client_sock.sendall(data.encode())
        loop(client_sock)

    accept()


if __name__ == '__main__':
    main()
