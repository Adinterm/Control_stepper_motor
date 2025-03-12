import tkinter as tk
import serial

# Configure the serial connection to Arduino
ser = serial.Serial('COM3', 9600)  # Replace 'COM3' with your Arduino port

# Send command to Arduino
current_command = None

def send_command(command):
    global current_command
    if current_command != command:
        try:
            ser.write(command.encode())
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
        # Reset focus to root so keyboard events work again
        root.focus_set()

# Stop motor

def stop_motor():
    global current_command
    send_command('X')  # 'X' is a general stop command for all motors
    current_command = None

# Create the GUI window
root = tk.Tk()
root.title("Stepper Motor Control")

# Speed input
speed_label = tk.Label(root, text="Speed:")
speed_label.pack(pady=5)
speed_entry = tk.Entry(root)
speed_entry.pack(pady=5)

# Bind Enter key to set speed
speed_entry.bind('<Return>', lambda event: send_speed())

send_speed_button = tk.Button(root, text="Set Speed", command=send_speed)
send_speed_button.pack(pady=5)

# Add buttons and bind keyboard keys to buttons
btn_up = tk.Button(root, text="Up", command=lambda: send_command('U'), width=10)
btn_up.pack(pady=5)
btn_down = tk.Button(root, text="Down", command=lambda: send_command('D'), width=10)
btn_down.pack(pady=5)
btn_left = tk.Button(root, text="Left", command=lambda: send_command('L'), width=10)
btn_left.pack(pady=5)
btn_right = tk.Button(root, text="Right", command=lambda: send_command('R'), width=10)
btn_right.pack(pady=5)
btn_release = tk.Button(root, text="Release All", command=stop_motor, width=10)
btn_release.pack(pady=5)

# Track key states to prevent multiple commands
key_states = {'Up': False, 'Down': False, 'Left': False, 'Right': False}

# Bind keyboard events to button actions
def on_key_press(event):
    if event.keysym == 'Up' and not key_states['Up']:
        key_states['Up'] = True
        send_command('U')
    elif event.keysym == 'Down' and not key_states['Down']:
        key_states['Down'] = True
        send_command('D')
    elif event.keysym == 'Left' and not key_states['Left']:
        key_states['Left'] = True
        send_command('L')
    elif event.keysym == 'Right' and not key_states['Right']:
        key_states['Right'] = True
        send_command('R')

def on_key_release(event):
    if event.keysym in key_states:
        key_states[event.keysym] = False
        stop_motor()

# Bind the events
root.bind('<KeyPress>', on_key_press)
root.bind('<KeyRelease>', on_key_release)

# Run the Tkinter event loop
root.geometry("300x350")
root.mainloop()
