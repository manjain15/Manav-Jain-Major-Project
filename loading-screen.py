import tkinter as tk
from tkinter import ttk
import itertools
import threading
import time

# Create the main window on the main thread
root = tk.Tk()  # This must be on the main thread
root.title("Loading...")
root.geometry("400x150")
root.eval("tk::PlaceWindow . center")

# Create the spinning wheel and progress bar
wheel_label = tk.Label(root, font=("Arial", 30))
wheel_label.pack()

progress_var = tk.IntVar()  # Variable for the progress bar
progress_bar = ttk.Progressbar(root, length=300, variable=progress_var, maximum=100)
progress_bar.pack(pady=20)

# Define a smoother wheel sequence using Unicode characters
wheel_sequence = itertools.cycle(["◐", "◓", "◑", "◒"])

# Define the function to update the spinning wheel
def update_wheel():
    wheel_label.configure(text=next(wheel_sequence))  # Update the spinning wheel
    root.after(100, update_wheel)  # Continue the animation every 100 ms

# Start the wheel animation on the main thread
update_wheel()

# Function to update the progress bar
def update_progress():
    if progress_var.get() < 100:
        progress_var.set(progress_var.get() + 10)  # Increment progress
        root.after(1000, update_progress)  # Call again after 1 second
    else:
        root.destroy()  # Close the loading screen when complete

# Start updating the progress bar
update_progress()

# Function to simulate fetching data in the background
def fetch_data():
    # Simulate a long-running task, like fetching data from an API
    time.sleep(5)
    # Data fetching logic goes here

# Fetch data in the background
fetch_thread = threading.Thread(target=fetch_data)
fetch_thread.start()

# Start the Tkinter main event loop
root.mainloop()

# Wait for the fetch thread to finish
fetch_thread.join()

# Once the loading screen closes and data is fetched, you can continue with your GUI logic
print("Data fetched, loading screen closed, proceeding with the next part of the program.")
