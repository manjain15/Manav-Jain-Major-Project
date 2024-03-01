import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
from typing import List
from tkinter import messagebox
import customtkinter as ctk
from CTkListbox import *
import requests
import zipfile
import io
import re
import redislite
import json
import datetime
from PIL import Image
import folium
from folium import plugins
import pygame.mixer
pygame.mixer.init()
from TransportNSW import TransportNSW
tnsw = TransportNSW()

redis_connection = redislite.Redis("/Users/manavjain/github-classroom/Baulkhamhills-hs/Manav-Jain-Major-Project/Trips", ":memory")

# CODE FOR PARSING SYDNEYTRAINS AND BUSES API
def get_gtfs_data(api_key, api_url):
    headers = {'Authorization': f'apikey {api_key}'}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        content_type = response.headers.get('Content-Type')

        if content_type or 'application/octet-stream' in content_type:
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
        while counter <= 37758:
                for key, val in parsed_bus_data["stops.txt"][counter].items():
                        if key == "stop_id":
                                stop_id = val
                        if key == "stop_name":
                                stop_name = val
                                bus_stops.update({stop_name:stop_id})
                counter+=1  

        counter1 = 0
        train_stops = {}
        while counter1 <= 1214:
                for key, val in parsed_train_data["stops.txt"][counter1].items():
                        if key == "stop_id":
                                station_id = val
                        if key == "stop_name":
                                station_name = val
                                train_stops.update({station_name:station_id})
                counter1+=1

        all_stops = bus_stops | train_stops

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

        # Play the startup sound
        pygame.mixer.music.load("startup_sound.mp3")
        pygame.mixer.music.play()

        # START OF GUI CODE
        class gui_handler:
                def __init__(self, master):
                        self.master = master
                        self.master.title("ViewTrip")
                        ctk.set_default_color_theme("black-gold.json")

                        self.current_screen = None

                        # Start Screen
                        self.show_start_screen()

                # CODE FOR FIRST SCREEN
                def show_start_screen(self):
                        if self.current_screen:
                                self.current_screen.destroy()

                        start_screen = ctk.CTkFrame(self.master)
                        start_screen.pack(side="top", fill="both", expand=True)

                        heading = ctk.CTkLabel(master=start_screen, justify="center", text="ViewTrip", font=("Helvetica", 20, "bold"))
                        heading.pack(side="top", fill="x", pady=10)

                        welcome_label = ctk.CTkLabel(master=start_screen, text="Welcome to ViewTrip", font=("Helvetica", 18, "underline"))
                        welcome_label.pack(pady=10)

                        welcome_information = ctk.CTkLabel(master=start_screen, text="To get started, press the plus button\n to add a new trip.", font=("Helvetica", 16, "italic"))
                        welcome_information.pack(pady=10)

                        my_image = ctk.CTkImage(light_image=Image.open('start_screen_logo.png'), dark_image=Image.open('start_screen_logo.png'), size=(200, 100))
                        image_label = ctk.CTkLabel(start_screen, text="", image=my_image)
                        image_label.pack(pady=10)

                        display_saved_trips = ctk.CTkButton(master=start_screen, text="Display Trips", command=self.show_display_saved_trips_screen)
                        display_saved_trips.pack(side="bottom", fill="x", pady=10)

                        add_new_trip = ctk.CTkButton(master=start_screen, text="+", command=lambda: self.show_selection_screen())
                        add_new_trip.pack(side="bottom", fill="x", pady=10)

                        self.current_screen = start_screen

                # CODE FOR SECOND SCREEN
                def show_selection_screen(self):
                        if self.current_screen:
                                self.current_screen.destroy()

                        selection_screen = ctk.CTkFrame(self.master)
                        selection_screen.pack(padx=10, pady=10)

                        ctk.CTkLabel(selection_screen, text="Select Starting Stop:").grid(row=0, column=0, padx=10, pady=10)

                        start_stations = list(all_stops.keys())
                        start_station_combobox = AutocompleteCombobox(selection_screen)
                        start_station_combobox.set_completion_list(start_stations)
                        start_station_combobox.grid(row=1, column=0, padx=10, pady=10)

                        ctk.CTkLabel(selection_screen, text="Select Destination Stop:").grid(row=2, column=0, padx=10, pady=10)

                        destination_stations = list(all_stops.keys())
                        destination_combobox = AutocompleteCombobox(selection_screen)
                        destination_combobox.set_completion_list(destination_stations)
                        destination_combobox.grid(row=3, column=0, padx=10, pady=10)

                        ctk.CTkLabel(selection_screen, text="What day would you like to depart?").grid(row=4, column=0, padx=10, pady=10)
                        departure_day_entry = ctk.CTkEntry(selection_screen, placeholder_text="YYYYMMDD")
                        departure_day_entry.grid(row=5, column=0, padx=10, pady=10, columnspan=8)

                        ctk.CTkLabel(selection_screen, text="What time would you like to depart?").grid(row=6, column=0, padx=10, pady=10)
                        departure_time_entry = ctk.CTkEntry(selection_screen, placeholder_text="HHDD (24 Hour Time)")
                        departure_time_entry.grid(row=7, column=0, padx=10, pady=10, columnspan=8)

                        ctk.CTkLabel(selection_screen, text="How many trip options would you like?").grid(row=8, column=0, padx=10, pady=10)
                        no_of_trips_entry = ctk.CTkEntry(selection_screen, placeholder_text="Enter a number greater than or equal to 1")
                        no_of_trips_entry.grid(row=9, column=0, padx=10, pady=10, columnspan=8)

                        def check_validity():
                                origin_valid = False
                                destination_valid = False
                                departure_date_valid = False
                                departure_time_valid = False
                                no_of_trips_valid = False

                                origin_text = start_station_combobox.get()
                                destination_text = destination_combobox.get()
                                departure_day_text = departure_day_entry.get()
                                departure_time_text = departure_time_entry.get()
                                no_of_trips_text = no_of_trips_entry.get()

                                if origin_text and destination_text and departure_day_text and departure_time_text and no_of_trips_text:
                                        if origin_text not in start_stations:
                                                origin_valid = False
                                                messagebox.showerror('INVALID INPUT', 'Error: Please enter a valid origin!')
                                                self.show_selection_screen()
                                        elif destination_text not in destination_stations:
                                                destination_valid = False
                                                messagebox.showerror('INVALID INPUT', 'Error: Please enter a valid destination!')
                                                self.show_selection_screen()
                                        
                                        elif int(no_of_trips_text) < 1:
                                                no_of_trips_valid = False
                                                messagebox.showerror('INVALID INPUT', 'Error: Please enter a valid number of trips!')
                                                self.show_selection_screen()

                                        else:
                                                origin_valid = True
                                                destination_valid = True
                                                no_of_trips_valid = True

                                                try:
                                                        datetime.datetime.strptime(departure_day_text, '%Y%m%d')
                                                        departure_date_valid = True

                                                except ValueError:
                                                        departure_date_valid = False
                                                        messagebox.showerror('INVALID INPUT', 'Error: Please enter a valid date format!')
                                                        self.show_selection_screen()

                                                try:
                                                        datetime.datetime.strptime(departure_time_text, '%H%M')
                                                        departure_time_valid = True

                                                except ValueError:
                                                        departure_time_valid = False
                                                        messagebox.showerror('INVALID INPUT', 'Error: Please enter a valid time format!')
                                                        self.show_selection_screen()
                                                        
                                else:
                                        messagebox.showerror('INVALID INPUT', 'Error: Please enter valid input for all fields!')
                                        self.show_selection_screen()

                                if origin_valid and destination_valid and departure_date_valid and departure_time_valid and no_of_trips_valid:
                                        self.show_train_screen(start_station_combobox.get(), destination_combobox.get(), departure_day_entry.get(), departure_time_entry.get(), int(no_of_trips_entry.get()))
                                        selection_screen.destroy()

                        next_button = ctk.CTkButton(selection_screen, text="Next", command=check_validity)
                        next_button.grid(row=10, column=0, columnspan=2, pady=10)
                        
                        back_button = ctk.CTkButton(selection_screen, text="Back", command=self.show_start_screen)
                        back_button.grid(row=11, column=0, columnspan=2, pady=10)

                        self.current_screen = selection_screen

                # CODE FOR THIRD SCREEN
                def show_train_screen(self, start_station, destination_station, departure_day, departure_time, no_of_trips):
                        if self.current_screen:
                                self.current_screen.destroy()


                        train_screen = tk.Frame(self.master)
                        train_screen.pack(padx=10, pady=10)

                        ctk.CTkLabel(train_screen, text=f"Trips from {start_station}").grid(row=0, column=0, pady=10)

                        tree = ttk.Treeview(train_screen, columns=("Journey", "Departure", "Arrival"), show="headings")
                        tree.column("Journey",anchor="center", width=95)
                        tree.heading("Journey", text="Journey")
                        tree.column("Departure",anchor="center", width=95)
                        tree.heading("Departure", text="Departure")
                        tree.column("Arrival",anchor="center", width=95)
                        tree.heading("Arrival", text="Arrival")
                        tree.grid(row=1, column=0, columnspan=2, pady=10)

                        # Handler for item click event
                        def on_item_click(event):
                                item_id = tree.focus()  # Get the ID of the clicked item
                                if item_id:  # Ensure that an item was clicked
                                        item_values = tree.item(item_id, "values")
                                        if item_values:
                                                self.show_detailed_journey_info_screen(trip_info_dict, item_values, start_station, destination_station, departure_day, departure_time, no_of_trips)


                        tree.bind("<ButtonRelease-1>", on_item_click)

                        start_stop_id = all_stops[start_station][1:]
                        destination_stop_id = all_stops[destination_station][1:]
                        train_info, trip_info_dict = self.get_train_info(start_stop_id, destination_stop_id, departure_day, departure_time, no_of_trips)

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
                                departure_time = journey["legs"][0]["origin"]["departureTimeEstimated"][11:16]
                                arrival_time = journey["legs"][-1]["destination"]["arrivalTimeEstimated"][11:16]

                                train_info.append((journey_no, departure_time, arrival_time))

                        return train_info, trip_info_dict

                def show_detailed_journey_info_screen(self, trip_info_dict, treeview_values, start_station, destination_station, departure_day, departure_time, no_of_trips):
                        if self.current_screen:
                                self.current_screen.destroy()

                        detailed_journey_screen = tk.Frame(self.master)
                        detailed_journey_screen.pack(padx=10, pady=10)

                        tree = ttk.Treeview(detailed_journey_screen, columns=("Transport", "Origin", "Departure", "Destination", "Arrival"), show="headings")
                        tree.column("Transport",anchor="center", width=50)
                        tree.heading("Transport", text="Transport")
                        tree.column("Origin",anchor="center", width=75)
                        tree.heading("Origin", text="Origin")
                        tree.column("Departure",anchor="center", width=50)
                        tree.heading("Departure", text="Departure")
                        tree.column("Destination",anchor="center", width=75)
                        tree.heading("Destination", text="Destination")
                        tree.column("Arrival",anchor="center", width=50)
                        tree.heading("Arrival", text="Arrival")
                        tree.grid(row=1, column=0, columnspan=5, pady=10)

                        train_info = []
                        coords = {}
                        journey_index = int(treeview_values[0]) - 1
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
                        m = folium.Map(location=map_center, zoom_start=4)

                        # Add markers for each coordinate
                        for name, coord in coords.items():
                                folium.Marker(location=coord, popup=name).add_to(m)

                        # Create an AntPath to represent the transport route
                        ant_path = plugins.AntPath(locations=coords.values(), color='blue')
                        m.add_child(ant_path)

                        # Save the map to an HTML file
                        m.save('map_with_coordinates.html')

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
                        
                        def save_trip():
                                all_keys = redis_connection.keys("*")
                                trip_id = f"{origin} to {destination}"
                                train_json = json.dumps(train_info)
                                redis_connection.set(trip_id, train_json)
                                self.show_start_screen()

                        # Back button to return to the previous screen
                        back_button = ctk.CTkButton(detailed_journey_screen, text="Back", command=lambda: self.show_train_screen(start_station, destination_station, departure_day, departure_time, no_of_trips))
                        back_button.grid(row=2, column=0, pady=10, columnspan=2)

                        save_trip_button = ctk.CTkButton(detailed_journey_screen, text="Save Trip", command=save_trip)
                        save_trip_button.grid(row=2, column=2, pady=10, columnspan=2)

                        self.current_screen = detailed_journey_screen

                def show_display_saved_trips_screen(self):
                        if self.current_screen:
                                self.current_screen.destroy()

                        display_saved_trips_screen = tk.Frame(self.master)
                        display_saved_trips_screen.pack(padx=10, pady=10)

                        all_keys = redis_connection.keys()

                        if all_keys == []:
                                ctk.CTkLabel(master=display_saved_trips_screen, text="Save a trip first").grid(pady=10)
                                def show_start_screen():
                                        self.show_start_screen()
                                        display_saved_trips_screen.destroy()
                                display_saved_trips_screen.after(3000, show_start_screen)

                        else:
                                trips_tree = ttk.Treeview(display_saved_trips_screen, columns=("Trip"), show="headings")
                                trips_tree.column("Trip",anchor="center", width=300)
                                trips_tree.heading("Trip", text="Trip")
                                trips_tree.grid(row=1, column=0, columnspan=5, pady=10)

                                for key in all_keys:
                                        key_str = key.decode('utf-8')
                                        trips_tree.insert("", "end", text=key_str, values=(key_str,))
                                
                                # Handler for item click event
                                def on_item_click(event):
                                        item_id = trips_tree.focus()  # Get the ID of the clicked item
                                        if item_id:  # Ensure that an item was clicked
                                                item_values = trips_tree.item(item_id, "values")
                                                if item_values:
                                                        self.show_saved_trip_detailed_screen(item_values)

                                trips_tree.bind("<ButtonRelease-1>", on_item_click)
                                
                                back_button = ctk.CTkButton(master=display_saved_trips_screen, text="Back", command=self.show_start_screen)
                                back_button.grid(row=2, column=0, columnspan=2, pady=10)

                                self.current_screen = display_saved_trips_screen

                def show_saved_trip_detailed_screen(self, treeview_values):
                        if self.current_screen:
                                self.current_screen.destroy()

                        saved_trip_detailed_screen = tk.Frame(self.master)
                        saved_trip_detailed_screen.pack(padx=10, pady=10)

                        detailed_trips_tree = ttk.Treeview(saved_trip_detailed_screen, columns=("Transport", "Origin", "Departure", "Destination", "Arrival"), show="headings")
                        detailed_trips_tree.column("Transport",anchor="center", width=50)
                        detailed_trips_tree.heading("Transport", text="Transport")
                        detailed_trips_tree.column("Origin",anchor="center", width=75)
                        detailed_trips_tree.heading("Origin", text="Origin")
                        detailed_trips_tree.column("Departure",anchor="center", width=50)
                        detailed_trips_tree.heading("Departure", text="Departure")
                        detailed_trips_tree.column("Destination",anchor="center", width=75)
                        detailed_trips_tree.heading("Destination", text="Destination")
                        detailed_trips_tree.column("Arrival",anchor="center", width=50)
                        detailed_trips_tree.heading("Arrival", text="Arrival")
                        detailed_trips_tree.grid(row=1, column=0, columnspan=5, pady=10)

                        desired_value = redis_connection.get(treeview_values[0])
                        decoded_desired_value = desired_value.decode("utf-8")
                        list_of_desired_values = json.loads(decoded_desired_value)

                        for value in list_of_desired_values:
                                detailed_trips_tree.insert("", "end", values=value)
                        
                        back_button = ctk.CTkButton(master=saved_trip_detailed_screen, text="Back", command=self.show_display_saved_trips_screen)
                        back_button.grid(row=2, column=0, columnspan=2, pady=10)

                        self.current_screen = saved_trip_detailed_screen

        if __name__ == "__main__":
                root = tk.Tk()
                root.wm_geometry("300x650")
                root.resizable(False, False)
                main = gui_handler(root)

                def on_closing():
                        redis_connection.flushdb()
                        print("Successfully flushed the database")
                        redis_connection.close()
                        print("Successfully closed the connection")
                        root.destroy()
                
                root.protocol("WM_DELETE_WINDOW", on_closing)

                root.mainloop()

if __name__ == "__main__":
        main()