from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint
from datetime import date, datetime, timedelta
import tkinter as tk
from tkinter import ttk
import random
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
    api_url = 'https://api.transport.nsw.gov.au/v1/gtfs/schedule/buses'
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
    gtfs_data = get_gtfs_data(api_key)
    parsed_data = parse_gtfs_data(gtfs_data)

    counter = 0
    stops = {}
    while counter <= 37763:
        for key, val in parsed_data["stops.txt"][counter].items():
            if key == "stop_id":
                stop_id = val
            if key == "stop_name":
                stop_name = val
                stops.update({stop_name:stop_id})
        counter+=1

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

            start_stations = list(stops.keys())
            start_station_combobox = AutocompleteCombobox(selection_screen)
            start_station_combobox.set_completion_list(start_stations)
            start_station_combobox.grid(row=0, column=1, padx=10, pady=10)

            ctk.CTkLabel(selection_screen, text="Select Destination Stop:").grid(row=1, column=0, padx=10, pady=10)

            destination_stations = list(stops.keys())
            destination_combobox = AutocompleteCombobox(selection_screen)
            destination_combobox.set_completion_list(destination_stations)
            destination_combobox.grid(row=1, column=1, padx=10, pady=10)

            show_trains_button = ctk.CTkButton(selection_screen, text="Next", command=lambda: self.show_train_screen(start_station_combobox.get(), destination_combobox.get()))
            show_trains_button.grid(row=2, column=0, columnspan=2, pady=10)

            self.current_screen = selection_screen

        # CODE FOR THIRD SCREEN
        def show_train_screen(self, start_station, destination_station):
            if self.current_screen:
                self.current_screen.destroy()

            train_screen = tk.Frame(self.master)
            train_screen.pack(padx=10, pady=10)

            ctk.CTkLabel(train_screen, text=f"Buses from {start_station}").grid(row=0, column=0, columnspan=2, pady=10)

            tree = ttk.Treeview(train_screen, columns=("Route", "Bus No.", "Departure", "Arrival"), show="headings")
            tree.column("Route",anchor="center", width=200)
            tree.heading("Route", text="Route")
            tree.column("Bus No.",anchor="center", width=200)
            tree.heading("Bus No.", text="Bus No.")
            tree.column("Departure",anchor="center", width=200)
            tree.heading("Departure", text="Departure")
            tree.column("Arrival",anchor="center", width=200)
            tree.heading("Arrival", text="Arrival")
            tree.grid(row=1, column=0, columnspan=4, pady=10)

            start_stop_id = stops[start_station][1:]
            destination_stop_id = stops[destination_station][1:]
            train_info = self.get_train_info(start_stop_id, destination_stop_id)

            for train in train_info:
                tree.insert("", "end", values=train)

            back_button = ctk.CTkButton(train_screen, text="Back", command=self.show_selection_screen)
            back_button.grid(row=2, column=0, pady=10)

            self.current_screen = train_screen

        # CODE TO RETRIEVE PARSED DATA FROM TNSW API
        def get_train_info(self, start_station, destination_station):
            # Configure API key authorization: APIKey
            configuration = swagger_client.Configuration()
            configuration.api_key['Authorization'] = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJwMWpGZWhGZTB4cHJiT05OMWxsenBHYUN1UkNhN1VIMGxNNTl4UDZURkpzIiwiaWF0IjoxNzAzMTM4ODY4fQ.1pTAXxfPAJ64BzqxaRU9xnFPflsJ0niKPDC6BBmDpkk'
            configuration.api_key_prefix['Authorization'] = 'apiKey'

            # create an instance of the API class
            api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
            output_format = 'rapidJSON' # str | Used to set the response data type. This documentation only covers responses that use the JSON format. Setting the `outputFormat` value to `rapidJSON` is required to enable JSON output. 
            coord_output_format = 'EPSG:4326' # str | This specifies the format the coordinates are returned in. While other variations are available, the `EPSG:4326` format will return the widely-used format.
            type_dm = 'stop' # str | This specifies the type of results expected based on the search input in `name_dm`. By specifying `any`, locations of all types can be returned. Typically, this API call is used for a specific stop, so `stop` should be used along with a stop ID or global stop ID in `name_dm`.  (default to stop)
            name_dm = start_station # str | This is the search term that will be used to find locations. If the combination of this value and `type_dm` results in more than one location found - or `mode` is not set to `direct`, then a list of stops and no departures will be returned. If `type_dm` is set to `stop` then this value can take a stop ID or a global stop ID.  (default to 10111010)
            mode = 'direct' # str | This allows the departure board to display directly without going through the stop verification process. Use this when the stop is known. This relies on the given combination of `type_dm` and `name_dm` returning only a single result, otherwise a list of stops and no departures shall be returned.  (optional) (default to direct)
            #name_key_dm = '$USEPOINT$' # str | Setting this parameter to `$USEPOINT$` enables you to request departures for a specific platform within a station. If this isn't used, then departures for all platforms at the stop specified in `name_dm` are returned.  (optional)
            itd_date = date.today().strftime("%Y%m%d") # str | The reference date used when searching trips, in `YYYYMMDD` format. For instance, 20160901 refers to 1 September 2016. Works in conjunction with the `itdTime` value. If not specified, the current server date is used.  (optional) (default to 20161001)
            itd_time = datetime.now().strftime("%H%M") # str | The reference time used when searching trips, in `HHMM` 24-hour format. For instance, 2215 refers to 10:15 PM. | Works in conjunction with the `itdDate` value. If not specified, the current server time is used.  (optional) (default to 1200)
            departure_monitor_macro = 'true' # str | Including this parameter enables a number of options that result in the departure monitor operating in the same way as the Transport for NSW Trip Planner web site. It is recommended this is enabled, along with the `TfNSWDM` parameter.  (optional) (default to true)
            excluded_means = 'checkbox' # str | This parameter which means of transport to exclude from the departure monitor. To exclude one means, select one of the following: `1` = train, `2` = metro, `4` = light rail, `5` = bus, `7` = coach, `9` = ferry, `11` = school bus. `checkbox` allows you to exclude more than one means of transport when used in conjunction with the `exclMOT_<ID>` parameters.  (optional)
            excl_mot_1 = '1' # str | Excludes train services from the departure monitor.  Must be used in conjunction with `excludedMeans=checkbox`  (optional)
            excl_mot_2 = '2' # str | Excludes metro services from the departure monitor.  Must be used in conjunction with `excludedMeans=checkbox`  (optional)
            excl_mot_4 = '4' # str | Excludes light rail services from the departure monitor.  Must be used in conjunction with `excludedMeans=checkbox`  (optional)
            #excl_mot_5 = '5' # str | Excludes bus services from the departure monitor.  Must be used in conjunction with `excludedMeans=checkbox`  (optional)
            excl_mot_7 = '7' # str | Excludes coach services from the departure monitor.  Must be used in conjunction with `excludedMeans=checkbox`  (optional)
            excl_mot_9 = '9' # str | Excludes ferry services from the departure monitor.  Must be used in conjunction with `excludedMeans=checkbox`  (optional)
            excl_mot_11 = '11' # str | Excludes school bus services from the departure monitor.  Must be used in conjunction with `excludedMeans=checkbox`  (optional)
            tf_nswdm = 'true' # str | Including this parameter enables a number of options that result in the departure monitor operating in the same way as the Transport for NSW Trip Planner web site, including enabling real-time data. It is recommended this is enabled, along with the `departureMonitorMacro` parameter.  (optional) (default to true)
            version = '10.2.1.42' # str | Indicates which version of the API the caller is expecting for both request and response data. Note that if this version differs from the version listed above then the returned data may not be as expected.  (optional) (default to 10.2.1.42)

            try:
                # Provides capability to provide NSW public transport departure information from a stop, station or wharf including real-time.
                api_response = api_instance.tfnsw_dm_request(output_format, coord_output_format, type_dm, name_dm, mode=mode, departure_monitor_macro=departure_monitor_macro, excluded_means=excluded_means, excl_mot_1=excl_mot_1, excl_mot_2=excl_mot_2, excl_mot_4=excl_mot_4, excl_mot_7=excl_mot_7, excl_mot_9=excl_mot_9, excl_mot_11=excl_mot_11, tf_nswdm=tf_nswdm, version=version)
                api_dictionary = api_response.__dict__
                #print(api_dictionary.keys()) --> dict_keys(['_error', '_locations', '_stop_events', '_version', 'discriminator'])
                # Assuming api_response is the dictionary response
                stop_events_data = api_dictionary['_stop_events']
                train_info = []

                for stop_event in stop_events_data:
                    stop_event_dict = stop_event.__dict__
                    departure_time = stop_event_dict['_departure_time_planned'][11:19]
                    location = stop_event_dict['_location']
                    location_name = location.name
                    transportation = stop_event_dict['_transportation']
                    transportation_description = transportation.description
                    route_name = transportation.disassembled_name
                    arrival_time = "Unknown"

                    train_info.append((transportation_description, route_name, departure_time, arrival_time))


            except ApiException as e:
                print("Exception when calling DefaultApi->tfnsw_dm_request: %s\n" % e)

            return train_info

    if __name__ == "__main__":
        root = tk.Tk()
        root.wm_geometry("500x500")
        main = ViewTrip(root)
        root.mainloop()

if __name__ == "__main__":
    main()
