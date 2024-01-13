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

starting_stop = "Albury Station"
destination_stop = "Aberdeen Station"

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
                    pass
                else:
                    station_name = val
            else:
                pass
        
        stations.update({station_name:station_id})
        counter+=1

    # START OF GUI CODE
    ctk.set_appearance_mode("System")

    # CODE FOR SCREEN WITH LIST OF ROUTES
    class trip_screen(tk.Frame):
        def __init__(self, *args, **kwargs):
            tk.Frame.__init__(self, *args, **kwargs)
            #p1 = add_trip(self)

            buttonframe = tk.Frame(self)
            container = tk.Frame(self)
            buttonframe.pack(side="top", fill="x", expand=False)
            container.pack(side="top", fill="both", expand=True)

            starting_stop_id = stations[starting_stop]
            destination_stop_id = stations[destination_stop]

            journey = tnsw.get_trip(starting_stop_id, destination_stop_id, 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJwMWpGZWhGZTB4cHJiT05OMWxsenBHYUN1UkNhN1VIMGxNNTl4UDZURkpzIiwiaWF0IjoxNzAzMTM4ODY4fQ.1pTAXxfPAJ64BzqxaRU9xnFPflsJ0niKPDC6BBmDpkk')
            due = str(journey["due"])
            departure_time = str(journey["departure_time"])
            arrival_time = str(journey["arrival_time"])

            time_till_arrival = ctk.CTkLabel(master=container, width=50, height=50, text=due + " minutes",bg_color="light blue", text_color="white")
            time_till_arrival.grid(column=0, row=1)

            starting_stop_label = ctk.CTkLabel(master=container, height=5, text=starting_stop)
            starting_stop_label.grid(column=1, row=0)

            departing = ctk.CTkLabel(master=container, text=departure_time[11:16] + " pm", width=50, height=45)
            departing.grid(column=1, row=1, padx=5)

            arriving = ctk.CTkLabel(master=container, text=arrival_time[11:16] + " pm", width=50, height=45)
            arriving.grid(column=6, row=1, padx=5)


        def show(self):
            self.lift() 

    # CODE FOR PAGE WHERE USERS CHOOSE DESTINATION STOP
    class choose_destination_stop(tk.Frame):
        def __init__(self, *args, **kwargs):
            tk.Frame.__init__(self, *args, **kwargs)
            p3 = trip_screen(self)

            buttonframe = tk.Frame(self)
            container = tk.Frame(self)
            container.option_add("*Font", "Times")
            buttonframe.pack(side="top", fill="x", expand=False)
            container.pack(side="top", fill="both", expand=True)

            p3.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

            def checkkey(event): 
                value = event.widget.get()

                # get data from stations 
                if value == '': 
                    data = stations.keys()
                else: 
                    data = [] 
                    for item in stations.keys(): 
                        if value.lower() in item.lower(): 
                            data.append(item)				 

                # update data in listbox 
                update(data) 

            def update(data):
                # clear previous data
                dropdown.delete(0, 'end') 
                # put new data 
                for item in data:
                    dropdown.insert('end', item) 
            
            # entry box
            entry = ctk.CTkEntry(master=container, placeholder_text="Enter destination stop...", width=300)
            entry.pack()
            entry.bind("<KeyRelease>", checkkey)

            # create scrollbar
            dropdown_frame = ctk.CTkFrame(container)
            scrollbar = tk.Scrollbar(dropdown_frame, orient="vertical")

            # creating list box 
            dropdown = tk.Listbox(dropdown_frame, width=40, yscrollcommand=scrollbar.set, font=("Times", 16))

            scrollbar.config(command=dropdown.yview)
            scrollbar.pack(side="right", fill="y")
            dropdown.pack() 
            dropdown_frame.pack()
            update(stations.keys())

            def change_text(txt):
                entry.delete(0,'end')
                entry.insert(0,txt)

            def get_destination_stop():
                global destination_stop
                destination_stop = entry.get()

            # binding double click on listbox item to paste value of selected item into entry box
            dropdown.bind("<Double-1>", lambda event: change_text(dropdown.get(dropdown.curselection())))

            # button to take user to next window 
            confirm_selection = ctk.CTkButton(master=container, text="Choose this stop", command=lambda: [p3.show(), get_destination_stop()])
            confirm_selection.pack()

        def show(self):
            self.lift() 

    # CODE FOR PAGE WHERE USERS CHOOSE STARTING STOP
    class choose_starting_stop(tk.Frame):
        def __init__(self, *args, **kwargs):
            tk.Frame.__init__(self, *args, **kwargs)
            p2 = choose_destination_stop(self)

            buttonframe = tk.Frame(self)
            container = tk.Frame(self)
            container.option_add("*Font", "Times")
            buttonframe.pack(side="top", fill="x", expand=False)
            container.pack(side="top", fill="both", expand=True)

            p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

            def checkkey(event): 
                value = event.widget.get()

                # get data from stations 
                if value == '': 
                    data = stations.keys()
                else: 
                    data = [] 
                    for item in stations.keys(): 
                        if value.lower() in item.lower(): 
                            data.append(item)				 

                # update data in listbox 
                update(data) 

            def update(data):
                # clear previous data
                dropdown.delete(0, 'end') 
                # put new data 
                for item in data:
                    dropdown.insert('end', item) 
            
            # entry box
            entry = ctk.CTkEntry(master=container, placeholder_text="Enter starting stop...", width=300)
            entry.pack()
            entry.bind("<KeyRelease>", checkkey)

            # create scrollbar
            dropdown_frame = ctk.CTkFrame(container)
            scrollbar = tk.Scrollbar(dropdown_frame, orient="vertical")

            # creating list box 
            dropdown = tk.Listbox(dropdown_frame, width=40, yscrollcommand=scrollbar.set, font=("Times", 16))

            scrollbar.config(command=dropdown.yview)
            scrollbar.pack(side="right", fill="y")
            dropdown.pack() 
            dropdown_frame.pack()
            update(stations.keys())

            def change_text(txt):
                entry.delete(0,'end')
                entry.insert(0,txt)

            def get_starting_stop():
                global starting_stop
                starting_stop = entry.get()

            # binding double click on listbox item to paste value of selected item into entry box
            dropdown.bind("<Double-1>", lambda event: change_text(dropdown.get(dropdown.curselection())))

            # button to take user to next window 
            confirm_selection = ctk.CTkButton(master=container, text="Choose this stop", command=lambda: [p2.show(), get_starting_stop()])
            confirm_selection.pack()

        def show(self):
            self.lift() 

    # CODE FOR MAIN SCREEN ( OPENS UPON STARTUP OF PROGRAM )
    class main_screen(tk.Frame):
        def __init__(self, *args, **kwargs):
            tk.Frame.__init__(self, *args, **kwargs)
            p1 = choose_starting_stop(self)

            buttonframe = tk.Frame(self)
            container = tk.Frame(self)
            buttonframe.pack(side="top", fill="x", expand=False)
            container.pack(side="top", fill="both", expand=True)

            p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

            heading = ctk.CTkLabel(master=container, justify="center", text="ViewTrip", corner_radius=10, )
            heading.pack(side="top", fill="x")

            add_new_trip = ctk.CTkButton(master=container, text="+", command=p1.show, corner_radius=10)
            add_new_trip.pack(side="bottom", fill="x")

            welcome_label = ctk.CTkLabel(master=container, text="Welcome to ViewTrip", bg_color="grey", corner_radius=10)
            welcome_label.pack(pady=10)

            welcome_information = ctk.CTkLabel(master=container, text="To get started, press the plus button to add a new trip.", bg_color="orange", corner_radius=10)
            welcome_information.pack()

    if __name__ == "__main__":
        root = tk.Tk()
        root.title("ViewTrip")
        main = main_screen(root)
        main.pack(side="top", fill="both", expand=True)
        root.wm_geometry("400x400")
        root.mainloop()

if __name__ == "__main__":
    main()