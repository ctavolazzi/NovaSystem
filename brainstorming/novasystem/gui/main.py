import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import datetime

def modern_gui():
    root = tk.Tk()
    root.title("NovaSystem GUI - Modern File Browser")
    root.geometry("800x600")  # Set initial size

    # Apply a modern theme
    style = ttk.Style(root)
    style.theme_use('clam')  # 'clam', 'alt', or 'vista' are good modern choices
    # Configure the treeview to have alternating row colors
    style.configure("Treeview", background="#D3D3D3", foreground="black", rowheight=25, fieldbackground="#D3D3D3")
    style.map("Treeview", background=[('selected', "#347083")])

    # Function to update the file list
    def update_file_list(path):
        file_list.delete(*file_list.get_children())
        try:
            for entry in os.scandir(path):
                if entry.is_dir():
                    icon = 'folder'
                else:
                    icon = 'file'
                file_list.insert('', 'end', text=entry.name, values=(icon, os.path.getsize(entry),
                    datetime.datetime.fromtimestamp(os.path.getmtime(entry)).strftime('%Y-%m-%d %H:%M:%S')))
        except PermissionError:
            messagebox.showerror("Permission Denied", f"You don't have permission to access this directory: {path}")

    # Function to change directory
    def change_directory():
        path = filedialog.askdirectory(initialdir=os.getcwd())
        if path:
            os.chdir(path)
            path_label.config(text=os.getcwd())
            update_file_list(path)

    # Function to refresh the current directory
    def refresh_directory():
        path = os.getcwd()
        update_file_list(path)

    # Function to handle file selection and preview
    def select_item(event):
        selected = file_list.focus()
        if selected:
            file_path = os.path.join(os.getcwd(), file_list.item(selected, 'text'))
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r') as file:
                        content = file.read(500)  # Read first 500 characters
                        file_preview.delete('1.0', tk.END)
                        file_preview.insert(tk.END, content)
                except Exception as e:
                    file_preview.delete('1.0', tk.END)
                    file_preview.insert(tk.END, f"Cannot preview this file: {e}")

    # Advanced File Operations Functions
    def delete_file():
        selected = file_list.focus()
        if selected:
            file_path = os.path.join(os.getcwd(), file_list.item(selected, 'text'))
            if messagebox.askyesno("Delete File", f"Are you sure you want to delete {file_path}?"):
                os.remove(file_path)
                refresh_directory()

    def create_new_file():
        file_name = filedialog.asksaveasfilename(defaultextension=".txt", initialdir=os.getcwd())
        if file_name:
            open(file_name, 'w').close()
            refresh_directory()

    # Search Functionality
    def search_files():
        query = search_entry.get()
        if query:
            update_file_list(os.getcwd(), query)
        else:
            refresh_directory()

    def update_file_list(path, search_query=None):
        file_list.delete(*file_list.get_children())
        try:
            for entry in os.scandir(path):
                if search_query and search_query.lower() not in entry.name.lower():
                    continue
                if entry.is_dir():
                    icon = 'folder'
                else:
                    icon = 'file'
                file_list.insert('', 'end', text=entry.name, values=(icon, os.path.getsize(entry),
                    datetime.datetime.fromtimestamp(os.path.getmtime(entry)).strftime('%Y-%m-%d %H:%M:%S')))
        except PermissionError:
            messagebox.showerror("Permission Denied", f"You don't have permission to access this directory: {path}")

    # UI Setup for Frames
    toolbar_frame = ttk.Frame(root)
    toolbar_frame.pack(fill='x', padx=5, pady=5)

    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=5, pady=5)

    # Left frame for the file list and scrollbar
    file_list_frame = ttk.Frame(main_frame)
    file_list_frame.pack(side='left', fill='both', expand=True)

    # Right frame for file preview
    preview_frame = ttk.Frame(main_frame)
    preview_frame.pack(side='right', fill='both', expand=True)



    # UI Elements
    welcome_label = tk.Label(root, text="Welcome to NovaSystem Enhanced File Browser", font=("Helvetica", 16))
    welcome_label.pack(pady=10)

    path_label = tk.Label(root, text=os.getcwd(), font=("Helvetica", 10))
    path_label.pack(pady=5)

    file_list = ttk.Treeview(root, columns=('Type', 'Size', 'Last Modified'))
    file_list.heading('#0', text='Name')
    file_list.heading('Type', text='Type')
    file_list.heading('Size', text='Size (bytes)')
    file_list.heading('Last Modified', text='Last Modified')
    file_list.column('#0', width=200)
    file_list.column('Type', width=100)
    file_list.column('Size', width=100)
    file_list.column('Last Modified', width=150)
    file_list.pack(pady=10)
    file_list.bind('<ButtonRelease-1>', select_item)

  # Toolbar Buttons
    change_dir_button = ttk.Button(toolbar_frame, text="Change Directory", command=change_directory)
    change_dir_button.pack(side='left', padx=2)

    refresh_button = ttk.Button(toolbar_frame, text="Refresh File List", command=refresh_directory)
    refresh_button.pack(side='left', padx=2)

    delete_button = ttk.Button(toolbar_frame, text="Delete File", command=delete_file)
    delete_button.pack(side='left', padx=2)

    new_file_button = ttk.Button(toolbar_frame, text="Create New File", command=create_new_file)
    new_file_button.pack(side='left', padx=2)

    search_entry = ttk.Entry(toolbar_frame)
    search_entry.pack(side='left', fill='x', expand=True, padx=2)

    search_button = ttk.Button(toolbar_frame, text="Search", command=search_files)
    search_button.pack(side='left', padx=2)

    # Add UI elements to their respective frames...
    ui_elements = {
        'change_dir': ("Change Directory", change_directory),
        'refresh': ("Refresh File List", refresh_directory),
        'delete': ("Delete File", delete_file),
        'create': ("Create New File", create_new_file),
        'search_entry': (None, None),
        'search': ("Search", search_files)
    }

    for element, (text, command) in ui_elements.items():
        if 'entry' in element:
            widget = ttk.Entry(toolbar_frame)
        else:
            widget = ttk.Button(toolbar_frame, text=text, command=command)
        widget.pack(side='left', padx=2, fill='x', expand=True if 'entry' in element else False)

    # Treeview with Scrollbar
    file_list_scrollbar = ttk.Scrollbar(file_list_frame, orient='vertical')
    file_list = ttk.Treeview(file_list_frame, columns=('Type', 'Size', 'Last Modified'), yscrollcommand=file_list_scrollbar.set)
    # Configure the scrollbar
    file_list_scrollbar.config(command=file_list.yview)
    file_list_scrollbar.pack(side='right', fill='y')
    file_list.pack(fill='both', expand=True)
    # Bind the select_item function to the treeview
    file_list.bind('<ButtonRelease-1>', select_item)

    # File Preview with Scrollbar
    preview_scrollbar = ttk.Scrollbar(preview_frame, orient='vertical')
    file_preview = tk.Text(preview_frame, yscrollcommand=preview_scrollbar.set, height=10)
    # Configure the scrollbar
    preview_scrollbar.config(command=file_preview.yview)
    preview_scrollbar.pack(side='right', fill='y')
    file_preview.pack(fill='both', expand=True)

    # Path label at the bottom
    path_label = ttk.Label(root, text=os.getcwd(), relief=tk.SUNKEN, anchor='w')
    path_label.pack(fill='x', side='bottom', padx=5, pady=5)

    # Initialize the file list
    update_file_list(os.getcwd())
    root.mainloop()
