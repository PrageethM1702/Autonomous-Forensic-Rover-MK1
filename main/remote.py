import socket
import tkinter as tk

# Server configuration
HOST = '192.168.69.204'  # Laptop's IP address
PORT = 8081              # Port to use

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server listening on {HOST}:{PORT}")

# Accept a connection
print("Waiting for ESP32 to connect...")
client_socket, client_address = server_socket.accept()
print(f"Connection from {client_address}")

# Function to send commands to the ESP32
def send_command(command):
    try:
        client_socket.sendall(command.encode() + b'\n')
        print(f"Sent command: {command}")
    except Exception as e:
        print(f"Failed to send command: {e}")

# Create the GUI
def create_gui():
    root = tk.Tk()
    root.title("ESP32 Motor Control")

    # Forward button
    forward_button = tk.Button(root, text="FORWARD", command=lambda: send_command("FORWARD"), height=2, width=10, bg="green")
    forward_button.grid(row=0, column=1, padx=5, pady=5)

    # Left button
    left_button = tk.Button(root, text="LEFT", command=lambda: send_command("LEFT"), height=2, width=10, bg="yellow")
    left_button.grid(row=1, column=0, padx=5, pady=5)

    # Stop button
    stop_button = tk.Button(root, text="STOP", command=lambda: send_command("STOP"), height=2, width=10, bg="red")
    stop_button.grid(row=1, column=1, padx=5, pady=5)

    # Right button
    right_button = tk.Button(root, text="RIGHT", command=lambda: send_command("RIGHT"), height=2, width=10, bg="yellow")
    right_button.grid(row=1, column=2, padx=5, pady=5)

    # Backward button
    backward_button = tk.Button(root, text="BACKWARD", command=lambda: send_command("BACKWARD"), height=2, width=10, bg="blue")
    backward_button.grid(row=2, column=1, padx=5, pady=5)

    root.mainloop()

# Run the GUI
create_gui()

# Close the socket when done
client_socket.close()
server_socket.close()
print("Server closed.")
