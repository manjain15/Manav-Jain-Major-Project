import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import random
import tkinter as tk
import customtkinter as ctk
from CTkListbox import *
import requests
import zipfile
import io
from io import StringIO
import re
from TransportNSW import TransportNSW
tnsw = TransportNSW()

# CODE FOR PARSING SYDNEYTRAINS API
def get_gtfs_data(api_key):
    api_url = 'https://api.transport.nsw.gov.au/v1/gtfs/schedule/sydneytrains'
    headers = {'Authorization': f'apikey {api_key}'}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200 and response.headers.get('Content-Type') == 'application/zip':
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            return {file_name: zip_file.read(file_name).decode("utf-8") for file_name in zip_file.namelist()}

    return None

def parse_gtfs_data(data):
    parsed_data = {}
    quoted_string_pattern = re.compile(r'"([^"]*?)"(?:,|$)')

    for file_name, file_content in data.items():
        lines = file_content.split('\n')

        # Skip the header row
        header_line = lines[0].strip('"').strip('\r')
        header = [match.group(1) for match in quoted_string_pattern.finditer(header_line)]

        if not header:
            header = [part.strip() for part in header_line.split(',') if part.strip()]

        file_name_without_extension = file_name.split('.')[0]
        file_id_header = f"{file_name_without_extension[:-1]}_id"
        if file_id_header not in header:
            header.insert(0, file_id_header)

        # Process rows excluding the header
        rows_data = [dict(zip(header, re.split('","|,",|,"|,"', row))) for row in lines[1:]]

        cleaned_rows = [{key: value for key, value in row.items() if value is not None} for row in rows_data]
        parsed_data[file_name] = cleaned_rows

    return parsed_data

def main():
    api_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJwMWpGZWhGZTB4cHJiT05OMWxsenBHYUN1UkNhN1VIMGxNNTl4UDZURkpzIiwiaWF0IjoxNzAzMTM4ODY4fQ.1pTAXxfPAJ64BzqxaRU9xnFPflsJ0niKPDC6BBmDpkk'
    gtfs_data = get_gtfs_data(api_key)
    parsed_data = parse_gtfs_data(gtfs_data)
    
    counter = 0
    stations = {}
    while counter < 1215:
        for key, val in parsed_data["stops.txt"][counter].items():
            if key == "stop_id":
                station_id = val[1:]
            if key == "stop_name":
                if "Platform" in val:
                    station_name = val
                    stations.update({station_name:station_id})
        counter+=1

    # START OF GUI CODE
    class ViewTrip:
        def __init__(self, master):
            self.master = master
            self.master.title("ViewTrip")

            self.current_screen = None

            # Start Screen
            self.show_start_screen()

        # CODE FOR FIRST SCREEN
        def show_start_screen(self):
            if self.current_screen:
                self.current_screen.destroy()

            start_screen = ctk.CTkFrame(self.master)
            start_screen.pack(padx=10, pady=10)

            ctk.CTkLabel(start_screen, text="Select Starting Station:").grid(row=0, column=0, padx=10, pady=10)

            start_stations = list(stations.keys())
            start_station_combobox = ttk.Combobox(start_screen, values=start_stations)
            start_station_combobox.grid(row=0, column=1, padx=10, pady=10)

            ctk.CTkLabel(start_screen, text="Select Destination Station:").grid(row=1, column=0, padx=10, pady=10)

            destination_stations = list(stations.keys())
            destination_combobox = ttk.Combobox(start_screen, values=destination_stations)
            destination_combobox.grid(row=1, column=1, padx=10, pady=10)

            show_trains_button = ctk.CTkButton(start_screen, text="Next", command=lambda: self.show_train_screen(start_station_combobox.get(), destination_combobox.get()))
            show_trains_button.grid(row=2, column=0, columnspan=2, pady=10)

            self.current_screen = start_screen

        # CODE FOR SECOND SCREEN
        def show_train_screen(self, start_station, destination_station):
            if self.current_screen:
                self.current_screen.destroy()

            train_screen = tk.Frame(self.master)
            train_screen.pack(padx=10, pady=10)

            ctk.CTkLabel(train_screen, text=f"Trains from {start_station} to {destination_station}").grid(row=0, column=0, columnspan=2, pady=10)

            tree = ttk.Treeview(train_screen, columns=("Train", "Departure", "Arrival"), show="headings")
            tree.heading("Train", text="Train")
            tree.heading("Departure", text="Departure")
            tree.heading("Arrival", text="Arrival")
            tree.grid(row=1, column=0, columnspan=2, pady=10)

            train_info = self.get_train_info(start_station, destination_station)

            for train in train_info:
                tree.insert("", "end", values=train)

            back_button = ctk.CTkButton(train_screen, text="Back", command=self.show_start_screen)
            back_button.grid(row=2, column=0, pady=10)

            self.current_screen = train_screen

        # CODE TO RETRIEVE PARSED DATA FROM TNSW API
        def get_train_info(self, start_station, destination_station):
            journey = tnsw.get_trip(stations[start_station], stations[destination_station], 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJwMWpGZWhGZTB4cHJiT05OMWxsenBHYUN1UkNhN1VIMGxNNTl4UDZURkpzIiwiaWF0IjoxNzAzMTM4ODY4fQ.1pTAXxfPAJ64BzqxaRU9xnFPflsJ0niKPDC6BBmDpkk')
            due = journey["due"]
            current_time = datetime.now()
            train_info = []

            for i in range(5):
                departure_time = current_time + timedelta(minutes=due)
                arrival_time = departure_time + timedelta(minutes=due)

                train_info.append((f"Train {i + 1}", departure_time.strftime('%H:%M'), arrival_time.strftime('%H:%M')))

            return train_info

    if __name__ == "__main__":
        root = tk.Tk()
        main = ViewTrip(root)
        root.mainloop()

if __name__ == "__main__":
    main()
