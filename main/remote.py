import socket
import tkinter as tk

HOST = '192.168.69.204'  # Laptop IP address
PORT = 8081   # Port

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server listening on {HOST}:{PORT}")

print("Waiting for ESP32 to connect...")
client_socket, client_address = server_socket.accept()
print(f"Connection from {client_address}")

def send_command(command):
    try:
        client_socket.sendall(command.encode() + b'\n')
        print(f"Sent command: {command}")
    except Exception as e:
        print(f"Failed to send command: {e}")

def create_gui():
    root = tk.Tk()
    root.title("ESP32 Motor Control")

    forward_button = tk.Button(root, text="FORWARD", command=lambda: send_command("FORWARD"), height=2, width=10, bg="green")
    forward_button.grid(row=0, column=1, padx=5, pady=5)

    left_button = tk.Button(root, text="LEFT", command=lambda: send_command("LEFT"), height=2, width=10, bg="yellow")
    left_button.grid(row=1, column=0, padx=5, pady=5)

    stop_button = tk.Button(root, text="STOP", command=lambda: send_command("STOP"), height=2, width=10, bg="red")
    stop_button.grid(row=1, column=1, padx=5, pady=5)

    right_button = tk.Button(root, text="RIGHT", command=lambda: send_command("RIGHT"), height=2, width=10, bg="yellow")
    right_button.grid(row=1, column=2, padx=5, pady=5)

    backward_button = tk.Button(root, text="BACKWARD", command=lambda: send_command("BACKWARD"), height=2, width=10, bg="blue")
    backward_button.grid(row=2, column=1, padx=5, pady=5)

    root.mainloop()

create_gui()

client_socket.close()
server_socket.close()
print("Server closed.")
