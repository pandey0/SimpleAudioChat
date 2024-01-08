import tkinter as tk
from tkinter import messagebox
import socket
import pyaudio
import _thread

class AudioChatClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Chat Client")

        self.server_ip_entry = tk.Entry(root)
        self.server_ip_entry.insert(0, "192.168.1.13")
        self.server_ip_entry.grid(row=0, column=0, padx=10, pady=10)

        self.connect_button = tk.Button(root, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=1, padx=10, pady=10)

        self.start_button = tk.Button(root, text="Start Audio Chat", command=self.start_audio_chat, state=tk.DISABLED)
        self.start_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.stop_button = tk.Button(root, text="Stop Audio Chat", command=self.stop_audio_chat, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 20000
        self.p = pyaudio.PyAudio()

        self.receive_stream = None
        self.send_stream = None

        self.s = None

    def connect_to_server(self):
        server_ip = self.server_ip_entry.get()
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((server_ip, 50000))
            self.connect_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.NORMAL)
            messagebox.showinfo("Connection", "Connected to the server.")
        except Exception as e:
            messagebox.showerror("Error", f"Error connecting to the server: {e}")

    def start_audio_chat(self):
        try:
            self.receive_stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS,
                                              rate=self.RATE, output=True, frames_per_buffer=self.CHUNK)
            self.send_stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS,
                                           rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            _thread.start_new_thread(self.receive_data, ())
            _thread.start_new_thread(self.send_data, ())
        except Exception as e:
            messagebox.showerror("Error", f"Error starting audio chat: {e}")

    def stop_audio_chat(self):
        try:
            if self.receive_stream:
                self.receive_stream.stop_stream()
                self.receive_stream.close()
            if self.send_stream:
                self.send_stream.stop_stream()
                self.send_stream.close()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Error stopping audio chat: {e}")

    def receive_data(self):
        while True:
            try:
                data = self.s.recv(1024)
                self.receive_stream.write(data)
            except:
                break

    def send_data(self):
        while True:
            try:
                data = self.send_stream.read(self.CHUNK)
                self.s.sendall(data)
            except:
                break

if __name__ == "__main__":
    root = tk.Tk()
    client_gui = AudioChatClientGUI(root)
    root.mainloop()
