import tkinter as tk
import socket
import select
import _thread

class AudioChatServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Chat Server")

        self.start_button = tk.Button(root, text="Start Server", command=self.start_server)
        self.start_button.grid(row=0, column=0, pady=10)

        self.stop_button = tk.Button(root, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.grid(row=1, column=0, pady=10)

        self.CONNECTION_LIST = []
        self.chat_server_socket = None

    def start_server(self):
        try:
            self.chat_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.chat_server_socket.bind(("0.0.0.0", 50000))
            self.chat_server_socket.listen(5)
            self.CONNECTION_LIST.append(self.chat_server_socket)

            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            _thread.start_new_thread(self.run_server, ())
            print("Server Started!")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error starting the server: {e}")

    def stop_server(self):
        try:
            if self.chat_server_socket:
                self.chat_server_socket.close()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error stopping the server: {e}")

    def broadcast(self, sock, data):
        for current_socket in self.CONNECTION_LIST:
            if current_socket != self.chat_server_socket and current_socket != sock:
                try:
                    current_socket.send(data)
                except:
                    pass

    def run_server(self):
        while True:
            rlist, wlist, xlist = select.select(self.CONNECTION_LIST, [], [])

            for current_socket in rlist:
                if current_socket is self.chat_server_socket:
                    (new_socket, address) = self.chat_server_socket.accept()
                    self.CONNECTION_LIST.append(new_socket)
                    print("%s connected to the server" % str(address))
                    _thread.start_new_thread(self.client_thread, (new_socket,))
                else:
                    try:
                        data = current_socket.recv(1024)
                        if data:
                            self.broadcast(current_socket, data)
                    except socket.error:
                        print("%s left the server" % str(address))
                        current_socket.close()
                        self.CONNECTION_LIST.remove(current_socket)

    def client_thread(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if data:
                    self.broadcast(client_socket, data)
            except socket.error:
                break

if __name__ == "__main__":
    root = tk.Tk()
    server_gui = AudioChatServerGUI(root)
    root.mainloop()
