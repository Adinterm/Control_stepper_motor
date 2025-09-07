import tkinter as tk
import serial

# Configure the serial connection to Arduino
ser = serial.Serial('COM7', 9600)  # Replace with your Arduino's port

# Track current command and idle timer
current_command = None
idle_after_id = None
IDLE_TIMEOUT_MS = 200  # Stop after 200ms of no movement

def send_command(command):
    global current_command
    if current_command != command:
        try:
            ser.write(f"{command}\n".encode())  # Send with newline
            print(f"Sent command: {command}")
            current_command = command
        except serial.SerialException as e:
            print(f"Serial error: {e}")

def send_speed():
    try:
        speed = int(speed_entry.get())
        if speed > 0:
            ser.write(f"S{speed}\n".encode())
            print(f"Speed set to: {speed}")
        else:
            print("Speed must be greater than 0")
    except ValueError:
        print("Invalid speed value")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    finally:
        root.focus_set()

def stop_motor():
    global current_command
    if current_command is not None:
        send_command('X')  # Stop command
        current_command = None

def schedule_idle_stop():
    global idle_after_id
    if idle_after_id:
        root.after_cancel(idle_after_id)
    idle_after_id = root.after(IDLE_TIMEOUT_MS, stop_motor)

# Mouse movement handler
def on_mouse_move(event):
    width = root.winfo_width()
    height = root.winfo_height()
    center_x = width / 2
    center_y = height / 2
    dx = event.x - center_x
    dy = event.y - center_y

    # Dead zone (to prevent jitter)
    dead_zone = 30
    if abs(dx) < dead_zone and abs(dy) < dead_zone:
        stop_motor()
        return

    if abs(dx) > abs(dy):
        if dx > 0:
            send_command('R')
        else:
            send_command('L')
    else:
        if dy > 0:
            send_command('D')
        else:
            send_command('U')

    schedule_idle_stop()  # Reset idle timer

# Stop motor when mouse leaves the window
def on_mouse_leave(event):
    stop_motor()

# Create the GUI window
root = tk.Tk()
root.title("Stepper Motor Control")

# Speed input
speed_label = tk.Label(root, text="Speed:")
speed_label.pack(pady=5)
speed_entry = tk.Entry(root)
speed_entry.pack(pady=5)
speed_entry.bind('<Return>', lambda event: send_speed())

send_speed_button = tk.Button(root, text="Set Speed", command=send_speed)
send_speed_button.pack(pady=5)

# Stop button
btn_release = tk.Button(root, text="Release All", command=stop_motor, width=15)
btn_release.pack(pady=10)

# Bind mouse movement and leave events
root.bind('<Motion>', on_mouse_move)
root.bind('<Leave>', on_mouse_leave)

# Set window size and run
root.geometry("400x400")
root.mainloop()
