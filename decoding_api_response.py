import json
from google.protobuf.json_format import MessageToJson
from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict
import requests

api_url = "https://api.transport.nsw.gov.au/v1/gtfs/vehiclepos/sydneytrains"
api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJwMWpGZWhGZTB4cHJiT05OMWxsenBHYUN1UkNhN1VIMGxNNTl4UDZURkpzIiwiaWF0IjoxNzAzMTM4ODY4fQ.1pTAXxfPAJ64BzqxaRU9xnFPflsJ0niKPDC6BBmDpkk"
headers = {"Authorization": f"apikey {api_key}"}

# Make a request to the API endpoint
response = requests.get(api_url, headers=headers)

# Extract the binary data from the response content
data = response.content

# Assuming 'data' contains the binary data
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(data)

# Convert the feed message to a dictionary
feed_dict = protobuf_to_dict(feed)
# print("About to print feed_dict")
# print(feed_dict)

# Convert the dictionary to JSON
json_data = json.dumps(feed_dict)
# print("About to print json_data")
# print(json_data)

# for entity in feed_dict["entity"]:
#     # print(entity)
#     for key, val in entity.items():
#         if key == "vehicle":
#             for key, val in val.items():
#                 if key == "vehicle":
#                     for key, val in val.items():
#                         if key == "label":
#                             if val == "3002":
#                                 print("Vehicle 3002 found")
#                                 print(entity["position"])

# Write JSON data to a file
with open('gtfs_realtime_feed.json', 'w') as json_file:
    json_file.write(json_data)

print("JSON data has been written to gtfs_realtime_feed.json")
