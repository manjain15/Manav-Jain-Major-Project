from pprint import pprint
from datetime import date, datetime, timedelta
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from CTkListbox import *
import requests
import zipfile
import io
import re
from TransportNSW import TransportNSW
tnsw = TransportNSW()

# CODE FOR PARSING SYDNEYTRAINS API
def get_gtfs_data(api_key, api_url):
    headers = {'Authorization': f'apikey {api_key}'}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        content_type = response.headers.get('Content-Type')

        if content_type and 'application/octet-stream' in content_type:
            try:
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                    return {file_name: zip_file.read(file_name).decode("utf-8") for file_name in zip_file.namelist()}
            except Exception as e:
                print(f"Error reading ZIP file: {e}")
        else:
            print("Unexpected content type. Expected 'application/octet-stream'.")
    else:
        print(f"API request failed with status code: {response.status_code}")
    
    return None

def parse_gtfs_data(data):
    if data is None:
        return None

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
    bus_data = get_gtfs_data(api_key, 'https://api.transport.nsw.gov.au/v1/gtfs/schedule/buses')
    train_data = get_gtfs_data(api_key, 'https://api.transport.nsw.gov.au/v1/gtfs/schedule/sydneytrains')
    parsed_bus_data = parse_gtfs_data(bus_data)
    parsed_train_data = parse_gtfs_data(train_data)

    counter = 0
    bus_stops = {}
    while counter <= 37763:
        for key, val in parsed_bus_data["stops.txt"][counter].items():
            if key == "stop_id":
                stop_id = val
            if key == "stop_name":
                stop_name = val
                bus_stops.update({stop_name:stop_id})
        counter+=1  

    counter1 = 0
    train_stops = {}

    # START OF AUTOCOMPLETE COMBOBOX CODE
    tkinter_umlauts=['odiaeresis', 'adiaeresis', 'udiaeresis', 'Odiaeresis', 'Adiaeresis', 'Udiaeresis', 'ssharp']

    class AutocompleteEntry(tk.Entry):
            """
            Subclass of tkinter.Entry that features autocompletion.

            To enable autocompletion use set_completion_list(list) to define
            a list of possible strings to hit.
            To cycle through hits use down and up arrow keys.
            """
            def set_completion_list(self, completion_list):
                    self._completion_list = sorted(completion_list, key=str.lower) # Work with a sorted list
                    self._hits = []
                    self._hit_index = 0
                    self.position = 0
                    self.bind('<KeyRelease>', self.handle_keyrelease)

            def autocomplete(self, delta=0):
                    """autocomplete the Entry, delta may be 0/1/-1 to cycle through possible hits"""
                    if delta: # need to delete selection otherwise we would fix the current position
                            self.delete(self.position, tk.END)
                    else: # set position to end so selection starts where textentry ended
                            self.position = len(self.get())
                    # collect hits
                    _hits = []
                    for element in self._completion_list:
                            if element.lower().startswith(self.get().lower()):  # Match case-insensitively
                                    _hits.append(element)
                    # if we have a new hit list, keep this in mind
                    if _hits != self._hits:
                            self._hit_index = 0
                            self._hits=_hits
                    # only allow cycling if we are in a known hit list
                    if _hits == self._hits and self._hits:
                            self._hit_index = (self._hit_index + delta) % len(self._hits)
                    # now finally perform the auto completion
                    if self._hits:
                            self.delete(0,tk.END)
                            self.insert(0,self._hits[self._hit_index])
                            self.select_range(self.position,tk.END)

            def handle_keyrelease(self, event):
                    """event handler for the keyrelease event on this widget"""
                    if event.keysym == "BackSpace":
                            self.delete(self.index(tk.INSERT), tk.END)
                            self.position = self.index(tk.END)
                    if event.keysym == "Left":
                            if self.position < self.index(tk.END): # delete the selection
                                    self.delete(self.position, tk.END)
                            else:
                                    self.position = self.position-1 # delete one character
                                    self.delete(self.position, tk.END)
                    if event.keysym == "Right":
                            self.position = self.index(tk.END) # go to end (no selection)
                    if event.keysym == "Down":
                            self.autocomplete(1) # cycle to next hit
                    if event.keysym == "Up":
                            self.autocomplete(-1) # cycle to previous hit
                    if len(event.keysym) == 1 or event.keysym in tkinter_umlauts:
                            self.autocomplete()

    class AutocompleteCombobox(ttk.Combobox):

            def set_completion_list(self, completion_list):
                    """Use our completion list as our drop down selection menu, arrows move through menu."""
                    self._completion_list = sorted(completion_list, key=str.lower) # Work with a sorted list
                    self._hits = []
                    self._hit_index = 0
                    self.position = 0
                    self.bind('<KeyRelease>', self.handle_keyrelease)
                    self['values'] = self._completion_list  # Setup our popup menu

            def autocomplete(self, delta=0):
                    """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
                    if delta: # need to delete selection otherwise we would fix the current position
                            self.delete(self.position, tk.END)
                    else: # set position to end so selection starts where textentry ended
                            self.position = len(self.get())
                    # collect hits
                    _hits = []
                    for element in self._completion_list:
                            if element.lower().startswith(self.get().lower()): # Match case insensitively
                                    _hits.append(element)
                    # if we have a new hit list, keep this in mind
                    if _hits != self._hits:
                            self._hit_index = 0
                            self._hits=_hits
                    # only allow cycling if we are in a known hit list
                    if _hits == self._hits and self._hits:
                            self._hit_index = (self._hit_index + delta) % len(self._hits)
                    # now finally perform the auto completion
                    if self._hits:
                            self.delete(0,tk.END)
                            self.insert(0,self._hits[self._hit_index])
                            self.select_range(self.position,tk.END)

            def handle_keyrelease(self, event):
                    """event handler for the keyrelease event on this widget"""
                    if event.keysym == "BackSpace":
                            self.delete(self.index(tk.INSERT), tk.END)
                            self.position = self.index(tk.END)
                    if event.keysym == "Left":
                            if self.position < self.index(tk.END): # delete the selection
                                    self.delete(self.position, tk.END)
                            else:
                                    self.position = self.position-1 # delete one character
                                    self.delete(self.position, tk.END)
                    if event.keysym == "Right":
                            self.position = self.index(tk.END) # go to end (no selection)
                    if len(event.keysym) == 1:
                            self.autocomplete()
                    # No need for up/down, we'll jump to the popup
                    # list at the position of the autocompletion

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
            start_screen.pack(side="top", fill="both", expand=True)

            heading = ctk.CTkLabel(master=start_screen, justify="center", text="ViewTrip", corner_radius=10, )
            heading.pack(side="top", fill="x")

            add_new_trip = ctk.CTkButton(master=start_screen, text="+", command=lambda: self.show_selection_screen(), corner_radius=10)
            add_new_trip.pack(side="bottom", fill="x")

            welcome_label = ctk.CTkLabel(master=start_screen, text="Welcome to ViewTrip", bg_color="grey", corner_radius=10)
            welcome_label.pack(pady=10)

            welcome_information = ctk.CTkLabel(master=start_screen, text="To get started, press the plus button to add a new trip.", bg_color="orange", corner_radius=10)
            welcome_information.pack()

            self.current_screen = start_screen

        # CODE FOR SECOND SCREEN
        def show_selection_screen(self):
            if self.current_screen:
                self.current_screen.destroy()

            selection_screen = ctk.CTkFrame(self.master)
            selection_screen.pack(padx=10, pady=10)

            ctk.CTkLabel(selection_screen, text="Select Starting Stop:").grid(row=0, column=0, padx=10, pady=10)

            start_stations = list(bus_stops.keys())
            start_station_combobox = AutocompleteCombobox(selection_screen)
            start_station_combobox.set_completion_list(start_stations)
            start_station_combobox.grid(row=0, column=1, padx=10, pady=10)

            ctk.CTkLabel(selection_screen, text="Select Destination Stop:").grid(row=1, column=0, padx=10, pady=10)

            destination_stations = list(bus_stops.keys())
            destination_combobox = AutocompleteCombobox(selection_screen)
            destination_combobox.set_completion_list(destination_stations)
            destination_combobox.grid(row=1, column=1, padx=10, pady=10)

            ctk.CTkLabel(selection_screen, text="What day would you like to depart?").grid(row=2, column=0, padx=10, pady=10)
            departure_day_entry = ctk.CTkEntry(selection_screen, placeholder_text="YYYYMMDD")
            departure_day_entry.grid(row=2, column=1, padx=10, pady=10)

            ctk.CTkLabel(selection_screen, text="What time would you like to depart?").grid(row=3, column=0, padx=10, pady=10)
            departure_time_entry = ctk.CTkEntry(selection_screen, placeholder_text="HHDD (24 Hour Time)")
            departure_time_entry.grid(row=3, column=1, padx=10, pady=10)

            ctk.CTkLabel(selection_screen, text="How many trip options would you like?").grid(row=4, column=0, padx=10, pady=10)
            no_of_trips_entry = ctk.CTkEntry(selection_screen, placeholder_text="Enter a number greater than or equal to 1")
            no_of_trips_entry.grid(row=4, column=1, padx=10, pady=10)

            show_trains_button = ctk.CTkButton(selection_screen, text="Next", command=lambda: self.show_train_screen(start_station_combobox.get(), destination_combobox.get(), departure_day_entry.get(), departure_time_entry.get(), no_of_trips_entry.get()))
            show_trains_button.grid(row=5, column=0, columnspan=2, pady=10)

            self.current_screen = selection_screen

        # CODE FOR THIRD SCREEN
        def show_train_screen(self, start_station, destination_station, departure_day, departure_time, no_of_trips):
            if self.current_screen:
                self.current_screen.destroy()

            train_screen = tk.Frame(self.master)
            train_screen.pack(padx=10, pady=10)

            ctk.CTkLabel(train_screen, text=f"Trips from {start_station}").grid(row=0, column=0, columnspan=3, pady=10)

            tree = ttk.Treeview(train_screen, columns=("Journey", "Departure", "Arrival"), show="headings")
            tree.column("Journey",anchor="center", width=200)
            tree.heading("Journey", text="Journey")
            tree.column("Departure",anchor="center", width=200)
            tree.heading("Departure", text="Departure")
            tree.column("Arrival",anchor="center", width=200)
            tree.heading("Arrival", text="Arrival")
            tree.grid(row=1, column=0, columnspan=3, pady=10)

            start_stop_id = bus_stops[start_station][1:]
            destination_stop_id = bus_stops[destination_station][1:]
            train_info, trip_info_dict = self.get_train_info(start_stop_id, destination_stop_id, departure_day, departure_time, no_of_trips)

            def on_item_click(event):
                item_id = tree.focus()  # Get the ID of the clicked item
                if item_id:  # Ensure that an item was clicked
                        item_values = tree.item(item_id, "values")
                
                self.show_detailed_journey_info_screen(trip_info_dict, item_values, start_station, destination_station, departure_day, departure_time, no_of_trips)
                

            tree.bind("<ButtonRelease-1>", on_item_click)

            for train in train_info:
                tree.insert("", "end", values=train)

            back_button = ctk.CTkButton(train_screen, text="Back", command=self.show_selection_screen)
            back_button.grid(row=2, column=0, pady=10)

            self.current_screen = train_screen

        # CODE TO RETRIEVE PARSED DATA FROM TNSW API
        def get_train_info(self, start_station, destination_station, departure_day, departure_time, no_of_trips):
                
                train_info = []

                def parse_api_response_to_dict(api_url, params, headers):
                        try:
                                # Make the request
                                response = requests.get(api_url, params=params, headers=headers)
                                
                                # Check if the request was successful (status code 200)
                                if response.status_code == 200:
                                        # Parse the JSON response into a dictionary
                                        data_dict = response.json()
                                        return data_dict
                                else:
                                        print(f"Error: {response.status_code} - {response.text}")
                                        return None
                        except Exception as e:
                                print(f"An error occurred: {e}")
                                return None

                # API endpoint
                api_url = "https://api.transport.nsw.gov.au/v1/tp/trip"

                # Parameters
                params = {
                        'outputFormat': 'rapidJSON',
                        'coordOutputFormat': 'EPSG:4326',
                        'depArrMacro': 'dep',
                        'itdDate': departure_day,
                        'itdTime': departure_time,
                        'type_origin': 'any',
                        'name_origin': start_station,
                        'type_destination': 'any',
                        'name_destination': destination_station,
                        'calcNumberOfTrips': no_of_trips,
                        'TfNSWTR': 'true',
                        'version': '10.2.1.42',
                        'itOptionsActive': '1',
                        'cycleSpeed': '16'
                }

                headers = {
                        'Authorization': 'apikey eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJwMWpGZWhGZTB4cHJiT05OMWxsenBHYUN1UkNhN1VIMGxNNTl4UDZURkpzIiwiaWF0IjoxNzAzMTM4ODY4fQ.1pTAXxfPAJ64BzqxaRU9xnFPflsJ0niKPDC6BBmDpkk'
                }

                # Parse API response into dictionary
                trip_info_dict = parse_api_response_to_dict(api_url, params, headers)
                journey_no = 0
                for journey in trip_info_dict["journeys"]:
                        journey_no += 1
                        departure_time = journey["legs"][0]["origin"]["departureTimeEstimated"][11:19]
                        arrival_time = journey["legs"][-1]["destination"]["arrivalTimeEstimated"][11:19]

                        train_info.append((journey_no, departure_time, arrival_time))

                return train_info, trip_info_dict
        
        def show_detailed_journey_info_screen(self, trip_info_dict, treeview_values, start_station, destination_station, departure_day, departure_time, no_of_trips):
            if self.current_screen:
                self.current_screen.destroy()

            detailed_journey_screen = tk.Frame(self.master)
            detailed_journey_screen.pack(padx=10, pady=10)

            tree = ttk.Treeview(detailed_journey_screen, columns=("Leg", "Transport", "Origin", "Departure", "Destination", "Arrival"), show="headings")
            tree.column("Leg",anchor="center", width=200)
            tree.heading("Leg", text="Leg")
            tree.column("Transport",anchor="center", width=200)
            tree.heading("Transport", text="Transport")
            tree.column("Origin",anchor="center", width=200)
            tree.heading("Origin", text="Origin")
            tree.column("Departure",anchor="center", width=200)
            tree.heading("Departure", text="Departure")
            tree.column("Destination",anchor="center", width=200)
            tree.heading("Destination", text="Destination")
            tree.column("Arrival",anchor="center", width=200)
            tree.heading("Arrival", text="Arrival")
            tree.grid(row=1, column=0, columnspan=5, pady=10)

            train_info = []
            journey_index = int(treeview_values[0])
            for key,val in trip_info_dict["journeys"][journey_index].items():
                  if key == "legs":
                        legs = val
                        i = 0
                        for leg in legs:
                            i += 1
                            transport = leg["transportation"].get("disassembledName")
                            if transport is None:
                                  transport = "Walking"
                            if transport == "M":
                                  transport == "Metro"
                            origin = leg["origin"]["name"]
                            departure = leg["origin"]["departureTimeEstimated"][11:19]
                            destination = leg["destination"]["name"]
                            arrival = leg["destination"]["arrivalTimeEstimated"][11:19]

                            train_info.append((i, transport, origin, departure, destination, arrival))
                  
                  journey_index +=1
            
            for train in train_info:
                tree.insert("", "end", values=train)   

            self.current_screen = detailed_journey_screen
                          

    if __name__ == "__main__":
        root = tk.Tk()
        root.wm_geometry("500x500")
        main = ViewTrip(root)
        root.mainloop()

if __name__ == "__main__":
    main()
