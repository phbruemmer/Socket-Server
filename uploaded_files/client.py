import socket
import struct
import time
import os
import encryption

host_name = socket.gethostname()
host = socket.gethostbyname(host_name)

server_ip = "127.0.0.1"

port = 6544

print(host_name)
print(host)
print(port)

BUFFER = 1024

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
    def check_server_space(f):
        """
        - Sends filename to server
        - Server response with boolean (True / False)
            (True if file does not exist / False if file exists)
        :param f:
        :return:
        """
        s.send(f.encode())
        time.sleep(.1)
        response = struct.unpack('?', s.recv(1))[0]
        print(response)                                                                                 # Debugging Help
        return response

    def ask_rename():
        """
        - send change name request to server
        - server starts change name sequence
        - send new name
        - server response with boolean (True / False)
            (If True continue program / If False ask for another name)
        :return:
        """
        rename_seq = False
        print("# # #\nF I L E - A L R E A D Y - E X I S T S\n# # #")
        rename = input("Do you want to rename the file? (y/n)")
        if rename == "y":
            rename_seq = True
        s.send(struct.pack('?', rename_seq))
        print(rename_seq)
        return rename_seq

    def rename_file():
        file_available = True
        print("# # #\nR E N A M E - F I L E\n# # #")
        new_file_name = input("(filename) > ")
        file_space = check_server_space(new_file_name)
        if not file_space:
            file_available = False
        return file_available, new_file_name

    print("# # # # # # #\nF I L E P A T H\n# # # # # # #\n")
    filepath = input("(filepath) > ")
    basename = os.path.basename(filepath)

    # Check if filepath exists
    if not os.path.exists(filepath):
        print("# # #\nN O - S U C H - P A T H - F O U N D\n# # #")
        return

    # Initialize upload sequence on server-side
    # Encrypt command with encryption.py - encrypt function (important)
    s.send(encryption.encrypt_data('$upload', True).encode())

    # Check if server-path is available or not
    server_space_available = check_server_space(basename)

    if not server_space_available:
        start_renaming = ask_rename()
        if not start_renaming:
            return
        new_filename_available, new_filename = rename_file()
        while not new_filename_available:
            new_filename_available, new_filename = rename_file()
        basename = new_filename

    # Send new / old filename
    s.send(basename.encode())

    with open(filepath, 'rb') as file:
        file_chunk = file.read(BUFFER)
        s.send(file_chunk)
        while file_chunk:
            print(file_chunk)
            file_chunk = file.read(BUFFER)
            s.send(file_chunk)
            print(file_chunk)
            time.sleep(.1)
        s.send("$upload-finished".encode())
        print("# F I L E - N O T - F O U N D #")


def file_downloader():
    download_dir = "./downloaded_files/"

    def check_filename(f):
        valid_file_ = False
        s.send(f.encode())
        time.sleep(.1)
        validation = s.recv(BUFFER).decode()
        if int(validation) > 0:
            valid_file_ = True
        return valid_file_

    def check_download_space(f):
        valid_space = False
        if os.path.exists(os.path.join(download_dir, f)):
            valid_space = True
        return valid_space

    def rename_file():
        print("# # #\nF I L E N A M E - N O T - A V A I L A B L E\n# # #")
        rename = input("Do you want to rename your local file? (y/n)")
        if rename == "n":
            return False
        print("# # #\nR E N A M E - F I L E\n# # #")
        new_file_name = input("(filename) > ")
        if check_download_space(new_file_name):
            rename_file()
        return new_file_name

    print("# # # # # # #\nF I L E N A M E\n# # # # # # #\n")
    filename = input("(filename) > ")
    download_file = filename
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    check = check_download_space(filename)
    print(check)
    if check:
        valid_file = rename_file()
        print(valid_file)
        if not valid_file:
            print(">>> Stopping download process...\n")
            return
        else:
            filename = valid_file
    s.send(encryption.encrypt_data('$download', True).encode())
    if not check_filename(download_file):
        print("# # #\nN O - S U C H - F I L E - F O U N D\n# # #")
        return
    with open(os.path.join(download_dir, filename), "wb") as file:
        file_data = s.recv(BUFFER)
        print(file_data.decode())
        while not file_data.decode() == "$download-finished":
            file.write(file_data)
            file_data = s.recv(BUFFER)
            print(file_data.decode())
            time.sleep(.1)


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
    elif msg == "$download":
        file_downloader()
    else:
        send(msg)
    chat()


def send(msg):
    msg = encryption.encrypt_data(msg, True)
    s.send(msg.encode())
    time.sleep(.1)
    recv()


def recv():
    msg = s.recv(BUFFER)
    msg = msg.decode()
    print(msg)
    msg = encryption.decrypt(msg)
    print(msg)


if __name__ == '__main__':
    main()
