import tkinter as tk
import pandas as pd
import csv
import time
from tkinter import ttk
from threading import Thread  # Import threading module
from main import runner  # Import runner function

# Replace with the path to your CSV file
csv_file = "processed_data.csv"

# Global variable to control the running state
running = False

def load_csv_data(csv_file):
    """Loads data from the CSV file and returns a list of dictionaries."""
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # Read the header row
        data = [dict(zip(header, row)) for row in reader]  # Create a list of dictionaries
    return data


def update_treeview(tree, data):
    """Clears the Treeview and inserts new data."""
    tree.delete(*tree.get_children())  # Clear existing data
    for i, item in enumerate(data, start=1):
        tags = ["evenrow" if i % 2 == 0 else "oddrow"]  # Alternate row colors
        tree.insert("", tk.END, values=(i, item["certificate_number"], item["value"], item["status"]), tags=tags)


def refresh_data(tree, csv_file, root):
    """Refreshes the Treeview with updated data from the CSV file."""
    data = load_csv_data(csv_file)
    update_treeview(tree, data)


def run_loop():
    """Runs the runner function in a loop while 'running' is True."""
    global running
    while running:
        runner()
        time.sleep(10)


def start_runner():
    """Starts the runner function in a separate thread."""
    global running
    running = True
    start_button.config(bg="red")  # Set button color to red
    runner_thread = Thread(target=run_loop)
    runner_thread.start()


def stop_runner():
    """Stops the runner function by setting 'running' to False."""
    global running
    running = False
    start_button.config(bg="green")  # Set button color to green


def exit_application():
    """Exits the application."""
    global running
    running = False  # Stop the runner
    root.quit()  # Quit the Tkinter main loop


def create_ui():
    """Creates the Tkinter UI to display processed data from a CSV file."""

    global root  # Declare 'root' as global (optional)
    global start_button  # Declare start_button as global to access it in start_runner

    root = tk.Tk()
    root.title("Stamp Automation")

    # Load initial data from the CSV file
    data = load_csv_data(csv_file)

    # Create a Treeview widget (from ttk module)
    tree = ttk.Treeview(root, columns=("index", "certificate_number", "value", "status"))
    tree.heading("index", text="Index")
    tree.heading("certificate_number", text="Certificate Number")
    tree.heading("value", text="Value")
    tree.heading("status", text="Status")
    tree.column("index", width=50)
    tree.column("certificate_number", width=150)
    tree.column("value", width=100)
    tree.column("status", width=100)
    tree.grid(row=0, column=0, sticky="nsew")

    # Apply styles
    style = ttk.Style()
    style.configure("Treeview", background="white", fieldbackground="white")
    style.configure("Treeview.Heading", background="lightblue")
    style.map("Treeview", foreground=[('selected', 'black'), ('active', 'blue')], background=[('selected', 'lightblue'), ('active', 'lightblue')])
    style.configure("evenrow", background="black", foreground="white")  # Set even row style
    style.configure("oddrow", background="gray", foreground="black")  # Set odd row style

    # Create Start, Stop, and Exit buttons
    start_button = tk.Button(root, text="Start", command=start_runner)
    start_button.grid(row=1, column=0, sticky="w")
    stop_button = tk.Button(root, text="Stop", command=stop_runner)
    stop_button.grid(row=1, column=1, sticky="e")
    exit_button = tk.Button(root, text="Exit", command=exit_application)
    exit_button.grid(row=1, column=2, sticky="e")

    # Create a Refresh button
    refresh_button = tk.Button(root, text="Refresh", command=lambda: refresh_data(tree, csv_file, root))
    refresh_button.grid(row=1, column=3, sticky="e")

    # Create a divider above the copyright label
    divider = ttk.Separator(root, orient=tk.HORIZONTAL)
    divider.grid(row=2, column=0, columnspan=4, sticky="ew")

    # Create a copyright label
    copyright_label = tk.Label(root, text="© 2023 NoblesseTech")
    copyright_label.grid(row=3, column=0, columnspan=4, sticky="nsew")  # Place at the bottom, span all columns

    # Insert initial data into the Treeview
    update_treeview(tree, data)

    # Configure the root window (optional)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    root.mainloop()


if __name__ == "__main__":
    create_ui()