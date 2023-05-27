import tkinter as tk

class Robot:
    def __init__(self):
        self.ascii_art = " 0.0 "
        self.window = None
        self.entry_field = None
        self.text_area = None

    def open_chat_window(self):
        self.window = tk.Toplevel()
        self.window.title("Robot Chat")
        self.text_area = tk.Text(self.window)
        self.text_area.insert(tk.END, self.ascii_art + "\n")
        self.text_area.pack()
        self.entry_field = tk.Entry(self.window)
        self.entry_field.bind("<Return>", self.handle_user_input)
        self.entry_field.pack()

    def handle_user_input(self, event):
        user_input = self.entry_field.get()
        self.text_area.insert(tk.END, "User: " + user_input + "\n")
        self.text_area.insert(tk.END, "Robot: " + user_input + "\n")  # Echoes back the user input
        self.entry_field.delete(0, tk.END)

# In the game loop, when the player comes into contact with a robot:
robot = Robot()
robot.open_chat_window()
