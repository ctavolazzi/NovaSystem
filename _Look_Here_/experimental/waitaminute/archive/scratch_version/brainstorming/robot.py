import tkinter as tk
import threading
import openai
from concurrent.futures import ThreadPoolExecutor

class Robot:
    def __init__(self, name, description, x_pos, y_pos, game):
        self.name = name
        self.description = description
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.ascii_art = "R"
        self.game = game
        self.loading = None
        self.loading_message = "Loading"
        self.messages = [{"role": "system", "content": f"You are a helpful robot named {self.name}."}]
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.is_streaming = False
        self.symbol = "R"

    def add_message(self, role, content):
        message = {"role": role, "content": content}
        self.messages.append(message)
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, f"{role}: {content}\n")
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)

    def send_user_message(self, event=None):
        user_input = self.user_input_entry.get()
        self.user_input_entry.delete(0, tk.END)

        if self.is_streaming:
            self.is_streaming = False
            return

        self.add_message("user", user_input)
        self.get_ai_response(user_input)

    def stream_message_to_chat(self, role, content, index=0):
        if index < len(content) and self.is_streaming:
            message = {"role": role, "content": content[:index + 1]}
            self.messages.append(message)
            self.chat_history.insert(tk.END, f"{role}: {content[:index + 1]}")
            self.chat_history.see(tk.END)
            self.chat_window.after(5, self.stream_message_to_chat, role, content, index + 1)
        else:
            self.add_instant_message(role, content)  # add the complete message
            self.is_streaming = False

    def open_chat_window(self):
        self.game.pause()
        self.start_chat()

    def start_chat(self):
        self.chat_window = tk.Toplevel()
        self.chat_window.minsize(300, 200)
        self.chat_window.maxsize(500, 400)
        self.chat_window.title(f"Chat with {self.name}")

        self.create_chat_interface()
        self.add_instant_message('assistant', f"{self.name}: Hello! What can I help you with today?\n")

    def create_chat_interface(self):
        self.create_chat_frame()
        self.create_chat_history()
        self.create_loading_label()
        self.create_user_input_entry()
        self.create_submit_button()

        self.chat_window.protocol("WM_DELETE_WINDOW", self.on_chat_close)

    def get_ai_response(self, user_input):
        self.start_loading_animation()
        future = self.executor.submit(self.make_openai_request, user_input)
        self.chat_window.after(100, self.check_openai_request, future)

    def make_openai_request(self, user_input):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        return response['choices'][0]['message']['content']

    def check_openai_request(self, future):
        if future.done():
            ai_response = future.result()
            self.stop_loading_animation()
            self.is_streaming = True
            self.stream_message_to_chat('assistant', ai_response)
        else:
            self.chat_window.after(100, self.check_openai_request, future)

    def start_loading_animation(self):
        self.loading_message = "Loading"
        self.loading = self.chat_window.after(500, self.update_loading_message, 0)

    def update_loading_message(self, dots=0):
        if dots < 3:
            dots += 1
        else:
            dots = 0

        self.loading_message = "Loading" + "." * dots
        self.loading_label.config(text=self.loading_message)
        self.loading = self.chat_window.after(500, self.update_loading_message, dots)

    def stop_loading_animation(self):
        if self.loading:
            self.chat_window.after_cancel(self.loading)
            self.loading = None
            self.loading_label.config(text="")

    def get_ai_response(self, user_input):
        self.start_loading_animation()
        future = self.executor.submit(self.make_openai_request, user_input)
        self.chat_window.after(100, self.check_openai_request, future)

    def create_chat_frame(self):
        self.chat_frame = tk.Frame(self.chat_window)
        self.chat_frame.pack(fill='both', expand=True)

    def create_chat_history(self):
        scrollbar = tk.Scrollbar(self.chat_frame)
        scrollbar.pack(side='right', fill='y')

        self.chat_history = tk.Text(self.chat_frame, state='disabled', width=50, height=15, wrap='word', yscrollcommand=scrollbar.set)
        self.chat_history.pack(fill='both', expand=True)

    def create_loading_label(self):
        self.loading_label = tk.Label(self.chat_window, text="")
        self.loading_label.pack()

    def create_user_input_entry(self):
        self.user_input_entry = tk.Entry(self.chat_window)
        self.user_input_entry.bind("<Return>", self.send_user_message)
        self.user_input_entry.pack()

    def create_submit_button(self):
        submit_button = tk.Button(self.chat_window, text="Submit", command=self.send_user_message)
        submit_button.pack()

    def on_chat_close(self):
        self.chat_window.destroy()
        self.game.unpause()

    def start_loading_animation(self):
        self.loading_message = "Loading"
        self.loading = self.chat_window.after(500, self.update_loading_message, 0)

    def open_chat_window(self):
        self.game.pause()
        self.start_chat()

    def on_chat_close(self):
        self.chat_window.destroy()
        self.game.unpause()
