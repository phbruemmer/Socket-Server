import socket
import struct
import time
import os
import encryption

HOST_NAME = socket.gethostname()
HOST = socket.gethostbyname(HOST_NAME)
SERVER_IP = "127.0.0.1"
PORT = 6544
BUFFER = 1024
DOWNLOAD_DIR = "./downloaded_files/"

print(HOST_NAME)
print(HOST)
print(PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def main():
    try:
        s.connect((SERVER_IP, PORT))
        print(f"Successfully connected to the Server. ({SERVER_IP}:{PORT})")
    except socket.error as e:
        print(f"Connection error: {e}\nTry to contact the server host. (Probably the Server is not online.)")
        exit(-1)

    chat()


def file_uploader():
    def check_server_space(f):
        """Check if server has space for the file and if file does not already exist."""
        s.send(f.encode())
        time.sleep(0.1)
        response = struct.unpack('?', s.recv(1))[0]
        print(response)  # Debugging Help
        return response

    def ask_rename():
        """Ask user if they want to rename the file if it already exists on the server."""
        rename_seq = False
        print("# # #\nF I L E - A L R E A D Y - E X I S T S\n# # #")
        rename = input("Do you want to rename the file? (y/n) ")
        if rename.lower() == "y":
            rename_seq = True
        s.send(struct.pack('?', rename_seq))
        print(rename_seq)
        return rename_seq

    def rename_file():
        """Handle file renaming process if the file already exists on the server."""
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

    # Using context manager for file operations
    with open(filepath, 'rb') as file:
        file_chunk = file.read(BUFFER)
        while file_chunk:
            s.send(file_chunk)
            print(file_chunk)  # Debugging Help
            file_chunk = file.read(BUFFER)
            time.sleep(0.1)

    s.send("$upload-finished".encode())
    print("# F I L E - N O T - F O U N D #")


def file_downloader():
    """Download a file from the server."""
    def check_filename(f):
        """Check if the file exists on the server."""
        valid_file_ = False
        s.send(f.encode())
        validation = s.recv(BUFFER).decode()
        if int(validation) > 0:
            valid_file_ = True
        return valid_file_

    def check_download_space(f):
        """Check if there is space available locally for the download."""
        return not os.path.exists(os.path.join(DOWNLOAD_DIR, f))

    def rename_file():
        """Handle renaming the file locally if needed."""
        print("# # #\nF I L E N A M E - N O T - A V A I L A B L E\n# # #")
        rename = input("Do you want to rename your local file? (y/n) ")
        if rename.lower() == "n":
            return False
        print("# # #\nR E N A M E - F I L E\n# # #")
        new_file_name = input("(filename) > ")
        if not check_download_space(new_file_name):
            return rename_file()
        return new_file_name

    print("# # # # # # #\nF I L E N A M E\n# # # # # # #\n")
    filename = input("(filename) > ")
    download_file = filename

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    if not check_download_space(filename):
        valid_file = rename_file()
        if not valid_file:
            print(">>> Stopping download process...\n")
            return
        filename = valid_file

    s.send(encryption.encrypt_data('$download', True).encode())

    if not check_filename(download_file):
        print("# # #\nN O - S U C H - F I L E - F O U N D\n# # #")
        return

    with open(os.path.join(DOWNLOAD_DIR, filename), "wb") as file:
        while True:
            file_data = s.recv(BUFFER)
            if file_data.decode() == "$download-finished":
                break
            file.write(file_data)
            print(file_data.decode())  # Debugging Help
            time.sleep(0.1)


def dirs():
    """Request the directory listing from the server."""
    s.send(encryption.encrypt_data("$dirs", True).encode())
    while True:
        data_ = s.recv(BUFFER).decode()
        if data_ == '$end-li':
            break
        print('- ' + data_)


def chat():
    """Main chat loop."""
    while True:
        msg = input("> ")

        if msg == "$exit":
            msg = encryption.encrypt_data("$exit", True)
            s.send(msg.encode())
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            break

        if msg == "$upload":
            file_uploader()
        elif msg == "$download":
            file_downloader()
        elif msg == "$dirs":
            dirs()
        else:
            send(msg)


def send(msg):
    """Send a message to the server."""
    msg = encryption.encrypt_data(msg, True)
    s.send(msg.encode())
    time.sleep(0.1)
    recv()


def recv():
    """Receive a message from the server."""
    msg = s.recv(BUFFER).decode()
    msg = encryption.decrypt(msg)
    print(msg)


if __name__ == '__main__':
    main()
