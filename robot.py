import openai
import tkinter as tk
import threading

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

    def open_chat_window(self):
        self.game.pause()
        self.start_chat()

    def start_chat(self):
        self.chat_window = tk.Toplevel()
        self.chat_window.minsize(300, 200)
        self.chat_window.maxsize(500, 400)
        self.chat_window.title(f"Chat with {self.name}")

        self.chat_frame = tk.Frame(self.chat_window)
        self.chat_frame.pack(fill='both', expand=True)

        scrollbar = tk.Scrollbar(self.chat_frame)
        scrollbar.pack(side='right', fill='y')

        self.chat_history = tk.Text(self.chat_frame, state='disabled', width=50, height=15, wrap='word', yscrollcommand=scrollbar.set)
        self.chat_history.pack(fill='both', expand=True)

        scrollbar.config(command=self.chat_history.yview)

        self.user_input_entry = tk.Entry(self.chat_window)
        self.user_input_entry.pack(side='bottom')

        submit_button = tk.Button(self.chat_window, text="Submit", command=self.send_message)
        submit_button.pack(side='bottom')

        self.chat_window.protocol("WM_DELETE_WINDOW", self.on_chat_close)
        self.chat_window.after(0, self.stream_to_label, f"{self.name}: Hello! What can I help you with today?\n", 0)

    def send_message(self):
        user_input = self.user_input_entry.get()
        self.user_input_entry.delete(0, 'end')
        self.add_message_to_chat(f"You: {user_input}")
        self.start_loading_animation()
        threading.Thread(target=self.stream_ai_response, args=(user_input,)).start()

    def start_loading_animation(self):
        self.add_message_to_chat(self.loading_message)
        self.loading = self.chat_window.after(500, self.update_loading_message, 0)

    def update_loading_message(self, dots):
        if dots < 3:
            dots += 1
        else:
            dots = 0

        self.loading_message = "Loading" + "." * dots
        self.update_last_message_in_chat(self.loading_message)
        self.loading = self.chat_window.after(500, self.update_loading_message, dots)

    def stop_loading_animation(self):
        if self.loading:
            self.chat_window.after_cancel(self.loading)
            self.loading = None
            self.delete_last_message_in_chat()

    def add_message_to_chat(self, message):
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, message + "\n")
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)

    def update_last_message_in_chat(self, message):
        self.chat_history.config(state='normal')
        self.chat_history.delete('end - 2 lines', 'end')
        self.chat_history.insert(tk.END, message + "\n")
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)

    def delete_last_message_in_chat(self):
        self.chat_history.config(state='normal')
        self.chat_history.delete('end - 2 lines', 'end')
        self.chat_history.config(state='disabled')

    def stream_ai_response(self, user_input):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are chatting with a friendly and helpful robot named {self.name}."},
                {"role": "user", "content": user_input}
            ]
        )

        response_message = f"{self.name}: {response['choices'][0]['message']['content']}"
        self.chat_window.after(0, self.stop_loading_animation)
        self.chat_window.after(0, self.stream_to_label, response_message, 0)

    def stream_to_label(self, message, index=0):
        if index < len(message):
            self.chat_history.config(state='normal')
            self.chat_history.insert(tk.END, message[index])
            self.chat_history.config(state='disabled')
            self.chat_window.after(35, self.stream_to_label, message, index + 1)

    def on_chat_close(self):
        self.game.resume()
        self.chat_window.destroy()
