import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter.constants import *
from typing import List
from tkinter import messagebox
import customtkinter as ctk
from CTkListbox import *
from tkcalendar import Calendar
import requests
import zipfile
import io
import re
import redislite
import json
import datetime
from datetime import datetime, timedelta
from PIL import Image
import folium
from folium import plugins
import webbrowser
import os
import time
import pygame.mixer
pygame.mixer.init()
from TransportNSW import TransportNSW
tnsw = TransportNSW()

# Establish a connection to the redis database
redis_connection = redislite.Redis("/Users/manavjain/github-classroom/Baulkhamhills-hs/Manav-Jain-Major-Project/Trips", ":memory")

# START OF AUTOCOMPLETE COMBOBOX CODE
class AutocompleteCombobox(ttk.Combobox):
        def __init__(self, *args, **kwargs):
                """Initialize the AutocompleteCombobox widget."""
                super().__init__(*args, **kwargs)
                self.set_completion_list([])
                self.bind('<KeyRelease>', self.handle_keyrelease)
        def set_completion_list(self, completion_list: List[str]) -> None:
                """Set the completion list for autocompletion."""
                self._completion_list = sorted(completion_list, key=str.lower)
                self._hits = []
                self._hit_index = 0
                self.position = 0
                self['values'] = self._completion_list
        def autocomplete(self, delta: int = 0) -> None:
                """Perform autocompletion based on the current input."""
                if delta:
                        self.delete(self.position, END)
                else:
                        self.position = len(self.get())
                _hits = []
                for element in self._completion_list:
                        if element.lower().startswith(self.get().lower()):
                                _hits.append(element)
                if _hits != self._hits:
                        self._hit_index = 0
                        self._hits = _hits
                if self._hits:
                        self.delete(0, END)
                        self.insert(0, self._hits[self._hit_index])
                        self.select_range(self.position, END)
        def handle_keyrelease(self, event: tk.Event) -> None:
                """Handle key release events and perform autocompletion."""
                if event.keysym == "BackSpace":
                        self.delete(self.index(INSERT), END)
                        self.position = self.index(END)
                elif event.keysym == "Left":
                        if self.position < self.index(END):
                                self.delete(self.position, END)
                        else:
                                self.position -= 1
                                self.delete(self.position, END)
                elif event.keysym == "Right":
                        self.position = self.index(END)
                elif len(event.keysym) == 1:
                        self.autocomplete()

# Retrievig GTFS data from the TNSW API
def get_gtfs_data(api_key, api_url, specific_file):
        headers = {'Authorization': f'apikey {api_key}'}

        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise an exception for non-200 status codes

        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                gtfs_data = {}
                for file_name in zip_file.namelist():
                        if specific_file and file_name != specific_file:
                                continue
                        gtfs_data[file_name] = zip_file.read(file_name).decode("utf-8")
                        return gtfs_data
    
        return None

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

# Retrieiving parsed data from the TNSW API
def get_train_info(api_key, start_station, destination_station, departure_day, departure_time, no_of_trips):
        
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
        
        headers = {'Authorization': f'apikey {api_key}'}
        
        # Parse API response into dictionary
        trip_info_dict = parse_api_response_to_dict(api_url, params, headers)
        journey_no = 0
        for journey in trip_info_dict["journeys"]:
                journey_no += 1
                departure_time = journey["legs"][0]["origin"]["departureTimeEstimated"][11:16]
                arrival_time = journey["legs"][-1]["destination"]["arrivalTimeEstimated"][11:16]
                train_info.append((journey_no, departure_time, arrival_time))
        
        return train_info, trip_info_dict

# Detailed tree view for both detailed_journey_info_screen and saved_trip_detailed_screen
def detailed_tree_view(screen):
        tree = ttk.Treeview(screen, columns=("Route", "Origin", "Departure", "Destination", "Arrival"), show="headings")
        tree.column("Route",anchor="center", width=50)
        tree.heading("Route", text="Route")
        tree.column("Origin",anchor="center", width=150)
        tree.heading("Origin", text="Origin")
        tree.column("Departure",anchor="center", width=75)
        tree.heading("Departure", text="Departure")
        tree.column("Destination",anchor="center", width=150)
        tree.heading("Destination", text="Destination")
        tree.column("Arrival",anchor="center", width=75)
        tree.heading("Arrival", text="Arrival")
        tree.grid(row=1, column=0, pady=10, padx=0)

        return tree

# Function to add 11 hours to Sydney time to convert to UTC time (for the API)
def add_hours_to_sydney_time(date_str, time_str):
    # Convert input strings to datetime object
    sydney_time = datetime.strptime(date_str + time_str, '%Y%m%d%H%M')
    
    # Add 11 hours to Sydney time
    sydney_time += timedelta(hours=11)
    
    # Return the result in the same format
    return sydney_time.strftime('%Y%m%d'), sydney_time.strftime('%H%M')

start_time_getting_bus_train_data = time.time()

# Load the API key from a JSON file
with open('api_key.json') as f:
        api_key_file = json.load(f)
api_key = api_key_file['API_KEY']

# Get bus and train data
start_getting_bus_data = time.time()
bus_data = get_gtfs_data(api_key, 'https://api.transport.nsw.gov.au/v1/gtfs/schedule/buses', specific_file="stops.txt")
end_getting_bus_data = time.time()
print(f"Time taken to get bus data: {end_getting_bus_data - start_getting_bus_data} seconds")

train_data = get_gtfs_data(api_key, 'https://api.transport.nsw.gov.au/v1/gtfs/schedule/sydneytrains', specific_file="stops.txt")
parsed_bus_data = parse_gtfs_data(bus_data, specific_file="stops.txt")
parsed_train_data = parse_gtfs_data(train_data, specific_file="stops.txt")

end_time_getting_bus_train_data = time.time()
print(f"Time taken to get bus and train data: {end_time_getting_bus_train_data - start_time_getting_bus_train_data} seconds")

# Create a dictionary of all stops
counter = 0
bus_stops = {}
while counter <= len(parsed_bus_data["stops.txt"]) - 1:
        for key, val in parsed_bus_data["stops.txt"][counter].items():
                if key == "stop_id":
                        stop_id = val
                if key == "stop_name":
                        stop_name = val
                        bus_stops.update({stop_name:stop_id})
        counter+=1  

counter1 = 0
train_stops = {}
while counter1 <= len(parsed_train_data["stops.txt"]) - 1:
        for key, val in parsed_train_data["stops.txt"][counter1].items():
                if key == "stop_id":
                        station_id = val
                if key == "stop_name":
                        station_name = val
                        train_stops.update({station_name:station_id})
        counter1+=1

all_stops = bus_stops | train_stops

# START OF GUI CODE
class gui_handler:
        def __init__(self, master):
                self.master = master
                self.master.title("ViewTrip")

                # Set the default color theme from JSON file
                ctk.set_default_color_theme("green-white.json")
                
                self.current_screen = None
                
                # Start Screen
                self.show_start_screen()
        
        # CODE FOR FIRST SCREEN
        def show_start_screen(self):
                if self.current_screen:
                        self.current_screen.destroy()
                
                start_screen = ctk.CTkFrame(self.master)
                start_screen.pack(side="top", fill="both", expand=True)
                
                heading = ctk.CTkLabel(master=start_screen, justify="center", text="ViewTrip")
                heading.pack(side="top", fill="x", pady=10)
                
                welcome_label = ctk.CTkLabel(master=start_screen, text="Welcome to ViewTrip")
                welcome_label.pack(pady=10)
                welcome_information = ctk.CTkLabel(master=start_screen, text="To get started, press the plus button\n to add a new trip.")
                welcome_information.pack(pady=10)
                
                start_screen_image = ctk.CTkImage(light_image=Image.open('start_screen_logo.png'), dark_image=Image.open('start_screen_logo.png'), size=(250, 130))
                image_label = ctk.CTkLabel(start_screen, text="", image=start_screen_image)
                image_label.pack(pady=10)

                display_saved_trips_image = ctk.CTkImage(light_image=Image.open('button_display-saved-trips.png'), dark_image=Image.open('button_display-saved-trips.png'), size=(196, 17))                
                display_saved_trips = ctk.CTkButton(master=start_screen, text="", image=display_saved_trips_image, command=self.show_display_saved_trips_screen)
                display_saved_trips.pack(side="bottom", pady=10)
                
                add_new_trip_image = ctk.CTkImage(light_image=Image.open('button_add-new-trip.png'), dark_image=Image.open('button_add-new-trip.png'), size=(87, 17))
                add_new_trip = ctk.CTkButton(master=start_screen, text="", image=add_new_trip_image, command=lambda: self.show_selection_screen())
                add_new_trip.pack(side="bottom", pady=10)
                
                self.current_screen = start_screen
        
        # CODE FOR SECOND SCREEN
        def show_selection_screen(self):
                if self.current_screen:
                        self.current_screen.destroy()
        
                selection_screen = ctk.CTkFrame(self.master)
                selection_screen.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Ensuring widgets will be centred within the screen
                selection_screen.grid_propagate(False)
                selection_screen.grid_columnconfigure(0, weight=1)
                selection_screen.grid_columnconfigure(4, weight=1)

                ctk.CTkLabel(selection_screen, text="Select Starting Stop:").grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
                start_stations = list(all_stops.keys())
                start_station_combobox = AutocompleteCombobox(selection_screen)
                start_station_combobox.set_completion_list(start_stations)
                start_station_combobox.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")
                
                ctk.CTkLabel(selection_screen, text="Select Destination Stop:").grid(row=3, column=2, padx=10, pady=10, sticky="nsew")
                destination_stations = list(all_stops.keys())
                destination_combobox = AutocompleteCombobox(selection_screen)
                destination_combobox.set_completion_list(destination_stations)
                destination_combobox.grid(row=4, column=2, padx=10, pady=10, sticky="nsew")

                cal = Calendar(selection_screen, selectmode = 'day', date_pattern = "yyyyMMdd", showweeknumbers=False ,
                               font="Calibri 13", cursor="hand1", background="black", foreground="white", headersbackground="white", 
                               headersforeground="white", selectbackground="orange", selectforeground="green", normalbackground="white",
                               normalforeground="white", weekendbackground="white", weekendforeground="white", othermonthbackground="white",)

                cal.grid(row=6, column=2, padx=10, pady=10, sticky="nsew")
                
                ctk.CTkLabel(selection_screen, text="What time would you like to depart?").grid(row=7, column=2, padx=10, pady=10, sticky="nsew")
                departure_time_entry = ctk.CTkEntry(selection_screen, placeholder_text="HHDD (24 Hour Time)")
                departure_time_entry.grid(row=8, column=2, padx=10, pady=10, sticky="nsew")
                
                ctk.CTkLabel(selection_screen, text="How many trip options would you like?").grid(row=9, column=2, padx=10, pady=10, sticky="nsew")
                no_of_trips_entry = ctk.CTkEntry(selection_screen, placeholder_text="Enter a number ≥ 1")
                no_of_trips_entry.grid(row=10, column=2, padx=10, pady=10, sticky="nsew")
                
                # Error checking for inputs in selection_screen (ensuring data validation)
                def check_validity():
                        # Initially setting all fields to invalid
                        origin_valid = False
                        destination_valid = False
                        departure_date_valid = False
                        departure_time_valid = False
                        no_of_trips_valid = False
                        
                        # Getting the text from the comboboxes and entries
                        origin_text = start_station_combobox.get()
                        destination_text = destination_combobox.get()
                        departure_day_text = cal.get_date()
                        print(departure_day_text)
                        departure_time_text = departure_time_entry.get()
                        no_of_trips_text = no_of_trips_entry.get()
                        
                        # Checking if user has inputted anything
                        if origin_text and destination_text and departure_day_text and departure_time_text and no_of_trips_text:
                                # Checking if the start and destination stations are valid and if not returning respective error messages
                                if origin_text not in start_stations:
                                        origin_valid = False
                                        messagebox.showerror('INVALID INPUT', 'Error: Please enter a valid origin!')
                                        self.show_selection_screen()
                                elif destination_text not in destination_stations:
                                        destination_valid = False
                                        messagebox.showerror('INVALID INPUT', 'Error: Please enter a valid destination!')
                                        self.show_selection_screen()
                                
                                # Checking if the number of trips is valid
                                elif int(no_of_trips_text) < 1:
                                        no_of_trips_valid = False
                                        messagebox.showerror('INVALID INPUT', 'Error: Please enter a valid number of trips!')
                                        self.show_selection_screen()
                                else:
                                        # If all inputs are valid, set the respective variables to True
                                        origin_valid = True
                                        destination_valid = True
                                        no_of_trips_valid = True
                                        # Checking if the date and time are valid
                                        try:
                                                datetime.strptime(departure_day_text, '%Y%m%d')
                                                departure_date_valid = True
                                        except ValueError:
                                                departure_date_valid = False
                                                messagebox.showerror('INVALID INPUT', 'Error: Please enter a valid date format!')
                                                self.show_selection_screen()
                                        try:
                                                datetime.strptime(departure_time_text, '%H%M')
                                                departure_time_valid = True
                                        except ValueError:
                                                departure_time_valid = False
                                                messagebox.showerror('INVALID INPUT', 'Error: Please enter a valid time format!')
                                                self.show_selection_screen()
                                                
                        else:
                                messagebox.showerror('INVALID INPUT', 'Error: Please enter valid input for all fields!')
                                self.show_selection_screen()
                        
                        # If all inputs are valid, show the train screen
                        if origin_valid and destination_valid and departure_date_valid and departure_time_valid and no_of_trips_valid:
                                self.show_train_screen(start_station_combobox.get(), destination_combobox.get(), cal.get_date(), departure_time_entry.get(), int(no_of_trips_entry.get()))
                                selection_screen.destroy()
                
                next_button_image = ctk.CTkImage(light_image=Image.open('button_next.png'), dark_image=Image.open('button_next.png'), size=(109, 17))
                next_button = ctk.CTkButton(selection_screen, text="", image=next_button_image, command=check_validity)
                next_button.grid(row=11, column=2, columnspan=2, pady=10)

                back_button_image = ctk.CTkImage(light_image=Image.open('button_back.png'), dark_image=Image.open('button_back.png'), size=(107, 17))
                back_button = ctk.CTkButton(selection_screen, text="", image=back_button_image, command=self.show_start_screen)
                back_button.grid(row=12, column=2, pady=10)
                
                self.current_screen = selection_screen
        
        # CODE FOR THIRD SCREEN
        def show_train_screen(self, start_station, destination_station, departure_day, departure_time, no_of_trips):
                if self.current_screen:
                        self.current_screen.destroy()
                
                train_screen = ctk.CTkFrame(self.master)
                train_screen.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Ensuring widgets will be centred within the screen
                train_screen.grid_propagate(False)
                train_screen.grid_columnconfigure(0, weight=1)
                train_screen.grid_columnconfigure(2, weight=1)

                ctk.CTkLabel(train_screen, text=f"Trips from {start_station}").grid(row=1, column=1, pady=10)

                tree = ttk.Treeview(train_screen, columns=("Journey", "Departure", "Arrival"), show="headings")
                tree.column("Journey",anchor="center", width=95)
                tree.heading("Journey", text="Journey")
                tree.column("Departure",anchor="center", width=95)
                tree.heading("Departure", text="Departure")
                tree.column("Arrival",anchor="center", width=95)
                tree.heading("Arrival", text="Arrival")
                tree.grid(row=2, column=1, pady=10)
                
                # Handler for item click event
                def on_item_click(event):
                        item_id = tree.focus()  # Get the ID of the clicked item
                        if item_id:  # Ensure that an item was clicked
                                item_values = tree.item(item_id, "values")
                                if item_values:
                                        self.show_detailed_journey_info_screen(trip_info_dict, item_values, start_station, destination_station, departure_day, departure_time, no_of_trips)
                
                tree.bind("<ButtonRelease-1>", on_item_click)
                
                global start_stop_id
                start_stop_id = all_stops[start_station][1:]

                global destination_stop_id
                destination_stop_id = all_stops[destination_station][1:]

                # Convert to UTC
                converted_date, converted_time = add_hours_to_sydney_time(departure_day, departure_time)

                train_info, trip_info_dict = get_train_info(api_key, start_stop_id, destination_stop_id, converted_date, converted_time, no_of_trips)
                
                for train in train_info:
                        tree.insert("", "end", values=train)
                
                back_button_image = ctk.CTkImage(light_image=Image.open('button_back.png'), dark_image=Image.open('button_back.png'), size=(107, 17))
                back_button = ctk.CTkButton(train_screen, text="", image=back_button_image, command=self.show_selection_screen)
                back_button.grid(row=3, column=1, pady=10)
                
                self.current_screen = train_screen
        
        def show_detailed_journey_info_screen(self, trip_info_dict, treeview_values, start_station, destination_station, departure_day, departure_time, no_of_trips):
                if self.current_screen:
                        self.current_screen.destroy()
                
                detailed_journey_screen = ctk.CTkFrame(self.master)
                detailed_journey_screen.pack(fill="both", expand=True, padx=10, pady=10)
                
                tree = detailed_tree_view(detailed_journey_screen)
                
                # Handler for item click event
                def on_item_click(event):
                        item_id = tree.focus()  # Get the ID of the clicked item
                        if item_id:  # Ensure that an item was clicked
                                item_values = tree.item(item_id, "values")
                                detailed_information = ctk.CTkLabel(detailed_journey_screen, text=(f"Route: {item_values[0]}\n Origin: {item_values[1]}\n Departure: {item_values[2]}\n Destination: {item_values[3]}\n Arrival: {item_values[4]}"))
                                detailed_information.grid(pady=10, padx=0)
                                detailed_journey_screen.after(3000, detailed_information.destroy)
                
                tree.bind("<ButtonRelease-1>", on_item_click)
                
                train_info = []
                coords = {}
                journey_index = int(treeview_values[0]) - 1
                original_journey_index = journey_index
                for leg in trip_info_dict["journeys"][journey_index]["legs"]:
                        for key,val in leg.items():
                                if key == "stopSequence":
                                        stops = val
                                        for stop in stops:
                                                stop_name = stop["name"]
                                                coord = stop["coord"]
                                                coords.update({stop_name:coord})
                
                # Create a map centered at the mean latitude and longitude of the coordinates
                map_center = [sum(coord[0] for coord in coords.values()) / len(coords.values()),
                        sum(coord[1] for coord in coords.values()) / len(coords.values())]
                
                # Create the map
                m = folium.Map(location=map_center, zoom_start=12)
                
                # Add markers for each coordinate
                for name, coord in coords.items():
                        folium.Marker(location=coord, popup=name).add_to(m)
                
                # Create an AntPath to represent the transport route
                ant_path = plugins.AntPath(locations=coords.values(), color='blue')
                m.add_child(ant_path)
                
                # Save the map to an HTML file
                m.save('route_map.html')       
                
                for key,val in trip_info_dict["journeys"][journey_index].items():
                        if key == "legs":
                                legs = val
                                for leg in legs:
                                        transport = leg["transportation"].get("disassembledName")
                                        if transport is None:
                                                transport = "Walk"
                                        if transport == "M":
                                                transport == "Metro"
                                        origin = leg["origin"]["name"]
                                        departure = leg["origin"]["departureTimeEstimated"][11:16]
                                        destination = leg["destination"]["name"]
                                        arrival = leg["destination"]["arrivalTimeEstimated"][11:16]
                                        # Append train information to the list
                                        train_info.append((transport, origin, departure, destination, arrival))
                                journey_index +=1
                
                for train in train_info:
                        tree.insert("", "end", values=train)
                
                origin = trip_info_dict["journeys"][original_journey_index]["legs"][0]["origin"]["name"]
                destination = trip_info_dict["journeys"][original_journey_index]["legs"][-1]["destination"]["name"]

                def save_trip():
                        trip_id = f"{origin} to {destination}"
                        train_json = json.dumps(train_info)
                        redis_connection.set(trip_id, train_json)
                        self.show_start_screen()
                
                # Back button to return to the previous screen
                back_button_image = ctk.CTkImage(light_image=Image.open('button_back.png'), dark_image=Image.open('button_back.png'), size=(107, 17))
                back_button = ctk.CTkButton(detailed_journey_screen, text="", image=back_button_image, command=lambda: self.show_train_screen(start_station, destination_station, departure_day, departure_time, no_of_trips))
                back_button.grid(row=2, column=0, pady=10, padx=5)
                
                save_trip_image = ctk.CTkImage(light_image=Image.open('button_save-trip.png'), dark_image=Image.open('button_save-trip.png'), size=(134, 17))
                save_trip_button = ctk.CTkButton(detailed_journey_screen, text="", image=save_trip_image , command=save_trip)
                save_trip_button.grid(row=3, column=0, pady=10, padx=5)

                # Display the map in a web browser
                def display_map():
                        filename = 'file:///'+os.getcwd()+'/' + 'route_map.html'
                        webbrowser.open_new_tab(filename)

                display_map_image = ctk.CTkImage(light_image=Image.open('button_display-map.png'), dark_image=Image.open('button_display-map.png'), size=(153, 19))
                display_map_button = ctk.CTkButton(detailed_journey_screen, text="", image=display_map_image, command=display_map)
                display_map_button.grid(row=4, column=0, pady=10, padx=5)

                self.current_screen = detailed_journey_screen
        
        def show_display_saved_trips_screen(self):
                if self.current_screen:
                        self.current_screen.destroy()
                
                display_saved_trips_screen = ctk.CTkFrame(self.master)
                display_saved_trips_screen.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Ensuring widgets will be centred within the screen
                display_saved_trips_screen.grid_propagate(False)
                display_saved_trips_screen.grid_columnconfigure(0, weight=1)
                display_saved_trips_screen.grid_columnconfigure(2, weight=1)

                all_keys = redis_connection.keys()
                
                if all_keys == []:
                        messagebox.showerror('INVALID INPUT', 'Error: Please save a trip first')
                        self.show_start_screen()
                        display_saved_trips_screen.destroy()
                else:
                        trips_tree = ttk.Treeview(display_saved_trips_screen, columns=("Trip"), show="headings")
                        trips_tree.column("Trip",anchor="center", width=300)
                        trips_tree.heading("Trip", text="Trip")
                        trips_tree.grid(row=1, column=1, pady=10)
                        
                        for key in all_keys:
                                key_str = key.decode('utf-8')
                                trips_tree.insert("", "end", text=key_str, values=(key_str,))
                        

                        # Handler for single click event
                        def on_single_click(event):
                                item_id = trips_tree.focus()
                                if item_id:
                                        item_values = list(trips_tree.item(item_id, "values"))

                        # Handler for double click event
                        def on_double_click(event):
                                item_id = trips_tree.focus()  # Get the ID of the clicked item
                                if item_id:  # Ensure that an item was clicked
                                        item_values = trips_tree.item(item_id, "values")
                                        if item_values:
                                                self.show_saved_trip_detailed_screen(item_values)

                        # Handler for deleting trip
                        def on_delete():
                                item_id = trips_tree.focus()
                                if item_id:
                                        redis_connection.delete(trips_tree.item(trips_tree.focus(), "text"))
                                        self.show_start_screen()
                                        display_saved_trips_screen.destroy()
                                else:
                                        messagebox.showerror('INVALID INPUT', 'Error: Please select a trip to delete')
                                        self.show_display_saved_trips_screen()
                        
                        trips_tree.bind("<Double-1>", on_double_click)
                        trips_tree.bind("<ButtonRelease-1>", on_single_click)
                        
                        back_button_image = ctk.CTkImage(light_image=Image.open('button_back.png'), dark_image=Image.open('button_back.png'), size=(107, 17))
                        back_button = ctk.CTkButton(master=display_saved_trips_screen, text="", image=back_button_image, command=self.show_start_screen)
                        back_button.grid(row=2, column=1, pady=10)

                        delete_button_image = ctk.CTkImage(light_image=Image.open('button_delete-trip.png'), dark_image=Image.open('button_delete-trip.png'), size=(107, 17))
                        delete_button = ctk.CTkButton(master=display_saved_trips_screen, text="", image=delete_button_image, command=on_delete)
                        delete_button.grid(row=3, column=1, pady=10)
                        
                        self.current_screen = display_saved_trips_screen
        
        def show_saved_trip_detailed_screen(self, treeview_values):
                if self.current_screen:
                        self.current_screen.destroy()
                
                saved_trip_detailed_screen = ctk.CTkFrame(self.master)
                saved_trip_detailed_screen.pack(fill="both", expand=True, padx=10, pady=10)
                
                detailed_trips_tree = detailed_tree_view(saved_trip_detailed_screen)

                current_date = datetime.now().strftime("%Y%m%d")
                current_time = datetime.now().strftime("%H%M")

                # Convert to UTC
                converted_date, converted_time = add_hours_to_sydney_time(current_date, current_time)

                train_info, trip_info_dict = get_train_info(api_key, start_stop_id, destination_stop_id, converted_date, converted_time, 3)

                train_info = []
                for key,val in trip_info_dict["journeys"][0].items():
                        if key == "legs":
                                legs = val
                                for leg in legs:
                                        transport = leg["transportation"].get("disassembledName")
                                        if transport is None:
                                                transport = "Walk"
                                        if transport == "M":
                                                transport == "Metro"
                                        origin = leg["origin"]["name"]
                                        departure = leg["origin"]["departureTimeEstimated"][11:16]
                                        destination = leg["destination"]["name"]
                                        arrival = leg["destination"]["arrivalTimeEstimated"][11:16]

                                        # Append train information to the list
                                        train_info.append((transport, origin, departure, destination, arrival))

                for train in train_info:
                        detailed_trips_tree.insert("", "end", values=train)

                # Handler for item click event
                def on_item_click(event):
                        item_id = detailed_trips_tree.focus()  # Get the ID of the clicked item
                        if item_id:  # Ensure that an item was clicked
                                item_values = detailed_trips_tree.item(item_id, "values")
                                detailed_information = ctk.CTkLabel(saved_trip_detailed_screen, text=(f"Route: {item_values[0]}\n Origin: {item_values[1]}\n Departure: {item_values[2]}\n Destination: {item_values[3]}\n Arrival: {item_values[4]}"))
                                detailed_information.grid(pady=10, padx=0)
                                saved_trip_detailed_screen.after(3000, detailed_information.destroy)
                
                detailed_trips_tree.bind("<ButtonRelease-1>", on_item_click)
                
                back_button_image = ctk.CTkImage(light_image=Image.open('button_back.png'), dark_image=Image.open('button_back.png'), size=(107, 17))
                back_button = ctk.CTkButton(master=saved_trip_detailed_screen, text="", image=back_button_image, command=self.show_display_saved_trips_screen)
                back_button.grid(row=2, column=0, columnspan=2, pady=10)
                
                self.current_screen = saved_trip_detailed_screen
    
def main():        
        # Play the startup sound
        pygame.mixer.music.load("startup_sound.mp3")
        pygame.mixer.music.play()

        root = tk.Tk()
        root.wm_geometry("505x710")
        root.resizable(False, False)
        main = gui_handler(root)
        def on_closing():
                redis_connection.flushdb()
                redis_connection.close()
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
        
if __name__ == "__main__":
        main()