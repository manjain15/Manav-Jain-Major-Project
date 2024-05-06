import tkinter as tk
from tkinter import ttk
import itertools
import threading
import time
import requests
import zipfile
import io
import json
import re

# Load the API key from a JSON file
with open('api_key.json') as f:
    api_key_file = json.load(f)
api_key = api_key_file['API_KEY']

# Retrieve GTFS data from the TNSW API
def get_gtfs_data(api_key, api_url, specific_file):
    headers = {'Authorization': f'apikey {api_key}'}

    response = requests.get(api_url, headers=headers)
    response.raise_for_status()  # Raise an exception for non-200 status codes

    gtfs_data = {}
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        for file_name in zip_file.namelist():
            if specific_file and file_name != specific_file:
                continue
            gtfs_data[file_name] = zip_file.read(file_name).decode("utf-8")
    
    return gtfs_data

# Parsing GTFS data
def parse_gtfs_data(data, specific_file):
    if data is None:
        return None
    
    parsed_data = {}
    quoted_string_pattern = re.compile(r'"([^"]*?)"(?:,|$)')
    
    for file_name, file_content in data.items():
        if specific_file and file_name != specific_file:
            continue
        
        lines = file_content.split('\n')
        
        # Skip empty lines
        lines = [line for line in lines if line.strip()]
        
        # Skip the header row if it exists
        header_line = lines[0].strip('"').strip('\r')
        header = [match.group(1) for match in quoted_string_pattern.finditer(header_line)] or header_line.split(',')
        
        file_name_without_extension = file_name.split('.')[0]
        file_id_header = f"{file_name_without_extension[:-1]}_id"
        
        if file_id_header not in header:
            header.insert(0, file_id_header)
        
        # Process rows excluding the header
        rows_data = [dict(zip(header, re.split('","|,",|,"|,"', row))) for row in lines[1:]]
        parsed_data[file_name] = rows_data
    
    return parsed_data

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

# Function to update the progress bar
def update_progress():
    if progress_var.get() < 100:
        progress_var.set(progress_var.get() + 10)  # Increment progress
        root.after(1000, update_progress)  # Call again after 1 second
    else:
        root.destroy()  # Close the loading screen when complete

# Shared variable to store the fetched data
data_container = {'data': None}

# Function to fetch data in the background
def get_parse_bus_data():
    # Record the start time
    start_time = time.time()

    # Fetch bus data
    bus_data = get_gtfs_data(api_key, 'https://api.transport.nsw.gov.au/v1/gtfs/schedule/buses', specific_file="stops.txt")
    print("Bus data fetched in:", time.time() - start_time)

    # Parse bus data
    data_container['bus'] = parse_gtfs_data(bus_data, specific_file="stops.txt")
    print("Bus data parsed in:", time.time() - start_time)

def get_parse_train_data():
    start_time = time.time()

    # Fetch train data
    train_data = get_gtfs_data(api_key, 'https://api.transport.nsw.gov.au/v1/gtfs/schedule/sydneytrains', specific_file="stops.txt")
    print("Train data fetched in:", time.time() - start_time)

    # Parse train data
    data_container['train'] = parse_gtfs_data(train_data, specific_file="stops.txt")
    print("Train data parsed in:", time.time() - start_time)

# Start the data fetch thread before starting the main loop
bus_thread = threading.Thread(target=get_parse_bus_data)
train_thread = threading.Thread(target=get_parse_train_data)

bus_thread.start()
train_thread.start()

# Start updating the progress bar and wheel
update_wheel()
update_progress()

# Start the Tkinter main event loop
root.mainloop()

# Wait for the fetch thread to finish
bus_thread.join()  # This ensures the thread completes before proceeding
train_thread.join()

# Access the parsed data
parsed_bus_data = data_container['bus']
parsed_train_data = data_container['train']
