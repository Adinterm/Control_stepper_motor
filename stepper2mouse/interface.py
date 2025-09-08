import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports

ser = None
current_command = None
idle_after_id = None
IDLE_TIMEOUT_MS = 200

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("tahoma", 8)
        )
        label.pack(ipadx=4, ipady=2)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def refresh_ports():
    ports = list_serial_ports()
    port_combo['values'] = ports
    if ports:
        port_combo.current(0)
    else:
        port_combo.set('')

def connect_serial():
    global ser
    port = port_combo.get()
    if not port:
        print("No port selected.")
        return
    try:
        ser = serial.Serial(port, 9600)
        print(f"Connected to {port}")
        connect_button.config(state=tk.DISABLED)
        disconnect_button.config(state=tk.NORMAL)
        port_combo.config(state=tk.DISABLED)
        refresh_button.config(state=tk.DISABLED)
        enable_controls()
    except serial.SerialException as e:
        print(f"Failed to connect: {e}")

def disconnect_serial():
    global ser
    stop_motor()
    if ser and ser.is_open:
        ser.close()
        print("Disconnected serial port.")

    ser = None
    port_combo.config(state=tk.NORMAL)
    connect_button.config(state=tk.NORMAL)
    disconnect_button.config(state=tk.DISABLED)
    refresh_button.config(state=tk.NORMAL)
    disable_controls()

def send_command(command):
    global current_command
    if ser and ser.is_open and current_command != command:
        try:
            ser.write(f"{command}\n".encode())
            print(f"Sent command: {command}")
            current_command = command
        except serial.SerialException as e:
            print(f"Serial error: {e}")

def send_speed():
    if not ser or not ser.is_open:
        return
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
        send_command('X')
        current_command = None

def schedule_idle_stop():
    global idle_after_id
    if idle_after_id:
        root.after_cancel(idle_after_id)
    idle_after_id = root.after(IDLE_TIMEOUT_MS, stop_motor)

def draw_center_cross():
    canvas.delete("cross")
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    center_x = width // 2
    center_y = height // 2
    canvas.create_line(center_x, 0, center_x, height, fill='gray', dash=(4, 2), tags="cross")
    canvas.create_line(0, center_y, width, center_y, fill='gray', dash=(4, 2), tags="cross")

def on_mouse_move(event):
    if not ser or not ser.is_open:
        return
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    center_x = width / 2
    center_y = height / 2
    dx = event.x - center_x
    dy = event.y - center_y

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

    schedule_idle_stop()

def on_mouse_leave(event):
    stop_motor()

def enable_controls():
    speed_label.config(state=tk.NORMAL)
    speed_entry.config(state=tk.NORMAL)
    send_speed_button.config(state=tk.NORMAL)
    btn_release.config(state=tk.NORMAL)
    canvas.bind('<Motion>', on_mouse_move)
    canvas.bind('<Leave>', on_mouse_leave)

def disable_controls():
    speed_label.config(state=tk.DISABLED)
    speed_entry.config(state=tk.DISABLED)
    send_speed_button.config(state=tk.DISABLED)
    btn_release.config(state=tk.DISABLED)
    canvas.unbind('<Motion>')
    canvas.unbind('<Leave>')

def add_placeholder(entry, placeholder_text):
    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.config(fg='gray')

    entry.insert(0, placeholder_text)
    entry.config(fg='gray')
    entry.bind('<FocusIn>', on_focus_in)
    entry.bind('<FocusOut>', on_focus_out)



# ------------------ GUI SETUP ------------------
root = tk.Tk()
root.title("Stepper Motor Control")

# COM port selection frame
port_frame = tk.Frame(root)
port_frame.pack(pady=5)

tk.Label(port_frame, text="Select Port:").pack(side=tk.LEFT, padx=5)

available_ports = list_serial_ports()
port_combo = ttk.Combobox(port_frame, values=available_ports, state="readonly", width=10)
port_combo.pack(side=tk.LEFT)
if available_ports:
    port_combo.current(0)

connect_button = tk.Button(port_frame, text="Connect", command=connect_serial)
connect_button.pack(side=tk.LEFT, padx=5)
ToolTip(connect_button, "Connect to selected COM port")

# 🔁 Refresh button
refresh_button = tk.Button(port_frame, text="🔄", command=refresh_ports)
refresh_button.pack(side=tk.LEFT, padx=2)
ToolTip(refresh_button, "Click to refresh COM ports")

# 🔌 Disconnect button
disconnect_button = tk.Button(port_frame, text="Disconnect", command=disconnect_serial)
disconnect_button.pack(side=tk.LEFT, padx=5)
disconnect_button.config(state=tk.DISABLED)
ToolTip(disconnect_button, "Disconnect from current port")

# Canvas for coordinate view
canvas = tk.Canvas(root, width=400, height=400, bg='white')
canvas.pack(fill=tk.BOTH, expand=True)
canvas.bind("<Configure>", lambda e: draw_center_cross())

# Speed controls
speed_label = tk.Label(root, text="Speed:")
speed_label.pack(pady=5)
speed_entry = tk.Entry(root)
speed_entry.pack(pady=5)
add_placeholder(speed_entry, "Default 60")

speed_entry.bind('<Return>', lambda event: send_speed())
send_speed_button = tk.Button(root, text="Set Speed", command=send_speed)
send_speed_button.pack(pady=5)

# Stop/Release button
btn_release = tk.Button(root, text="Release All", command=stop_motor, width=15)
btn_release.pack(pady=10)

# Disable motor controls until connected
disable_controls()

# Window size
root.geometry("450x550")
root.mainloop()
