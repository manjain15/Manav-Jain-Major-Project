import requests

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

if __name__ == "__main__":
    # API endpoint
    api_url = "https://api.transport.nsw.gov.au/v1/tp/trip"

    # Parameters
    params = {
        'outputFormat': 'rapidJSON',
        'coordOutputFormat': 'EPSG:4326',
        'depArrMacro': 'dep',
        'itdDate': '20240203',
        'itdTime': '1800',
        'type_origin': 'any',
        'name_origin': '2153482',
        'type_destination': 'any',
        'name_destination': '2150114',
        'calcNumberOfTrips': '2',
        'TfNSWTR': 'true',
        'version': '10.2.1.42',
        'itOptionsActive': '1',
        'cycleSpeed': '16'
    }

    # Headers with your API key (replace 'YOUR_API_KEY' with your actual API key)
    headers = {
        'Authorization': 'apikey eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJwMWpGZWhGZTB4cHJiT05OMWxsenBHYUN1UkNhN1VIMGxNNTl4UDZURkpzIiwiaWF0IjoxNzAzMTM4ODY4fQ.1pTAXxfPAJ64BzqxaRU9xnFPflsJ0niKPDC6BBmDpkk'
    }

    # Parse API response into dictionary
    trip_info_dict = parse_api_response_to_dict(api_url, params, headers)
    departure_name = trip_info_dict["journeys"][0]["legs"][0]["origin"]["name"]
    departure_time = trip_info_dict["journeys"][0]["legs"][0]["origin"]["departureTimeEstimated"]
    arrival_name = trip_info_dict["journeys"][0]["legs"][0]["destination"]["name"]
    arrival_time = trip_info_dict["journeys"][0]["legs"][0]["destination"]["arrivalTimeEstimated"]
    route_name = trip_info_dict["journeys"][0]["legs"][0]["transportation"]["disassembledName"]
    departure_name1 = trip_info_dict["journeys"][1]["legs"][0]["origin"]["name"]
    departure_time1 = trip_info_dict["journeys"][1]["legs"][0]["origin"]["departureTimeEstimated"]
    arrival_name1 = trip_info_dict["journeys"][1]["legs"][0]["destination"]["name"]
    arrival_time1 = trip_info_dict["journeys"][1]["legs"][0]["destination"]["arrivalTimeEstimated"]
    route_name1 = trip_info_dict["journeys"][1]["legs"][0]["transportation"]["disassembledName"]

    print(trip_info_dict)
    # print(departure_name)
    # print(departure_time)
    # print(arrival_name)
    # print(arrival_time)
    # print(route_name)

    # print(departure_name1)
    # print(departure_time1)
    # print(arrival_name1)
    # print(arrival_time1)
    # print(route_name1)