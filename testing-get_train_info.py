import unittest
from unittest.mock import patch, MagicMock
import requests
from main import get_train_info  # Adjust as needed

class TestGetTrainInfo(unittest.TestCase):
    @patch('requests.get')
    def test_get_train_info_success(self, mock_get):
        # Create a mock response with a 200 status code and sample JSON data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "journeys": [
                {
                    "legs": [
                        {
                            "origin": {
                                "departureTimeEstimated": "2024-05-07T14:30:00"
                            },
                            "destination": {
                                "arrivalTimeEstimated": "2024-05-07T16:30:00"
                            }
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        api_key = 'testapikey'
        start_station = 'Sydney Central'
        destination_station = 'Newcastle'
        departure_day = '20240518'
        departure_time = '1115'
        no_of_trips = 1

        # Print inputs
        print("test_get_train_info_success:")
        print("Inputs:")
        print(f"  api_key: {api_key}")
        print(f"  start_station: {start_station}")
        print(f"  destination_station: {destination_station}")
        print(f"  departure_day: {departure_day}")
        print(f"  departure_time: {departure_time}")
        print(f"  no_of_trips: {no_of_trips}")

        train_info, trip_info_dict = get_train_info(api_key, start_station, destination_station, departure_day, departure_time, no_of_trips)
        
        # Print outputs
        print("Outputs:")
        print(f"  train_info: {train_info}")
        print(f"  trip_info_dict: {trip_info_dict}")

        try:
            self.assertEqual(len(train_info), 1)
            self.assertEqual(train_info[0], (1, '14:30', '16:30'))
            self.assertIsNotNone(trip_info_dict)
            print("  Result: Successful\n")
        except AssertionError as e:
            print(f"  Result: Unsuccessful - {str(e)}\n")

    @patch('requests.get')
    def test_get_train_info_error(self, mock_get):
        # Mock a non-200 response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = 'Not Found'
        mock_get.return_value = mock_response
        
        api_key = 'testapikey'
        start_station = 'Sydney Central'
        destination_station = 'Newcastle'
        departure_day = '20240507'
        departure_time = '1430'
        no_of_trips = 1

        # Print inputs
        print("test_get_train_info_error:")
        print("Inputs:")
        print(f"  api_key: {api_key}")
        print(f"  start_station: {start_station}")
        print(f"  destination_station: {destination_station}")
        print(f"  departure_day: {departure_day}")
        print(f"  departure_time: {departure_time}")
        print(f"  no_of_trips: {no_of_trips}")

        train_info, trip_info_dict = get_train_info(api_key, start_station, destination_station, departure_day, departure_time, no_of_trips)

        # Print outputs
        print("Outputs:")
        print(f"  train_info: {train_info}")
        print(f"  trip_info_dict: {trip_info_dict}")

        try:
            self.assertEqual(len(train_info), 0)
            self.assertIsNone(trip_info_dict)
            print("  Result: Successful\n")
        except AssertionError as e:
            print(f"  Result: Unsuccessful - {str(e)}\n")

    @patch('requests.get')
    def test_get_train_info_exception(self, mock_get):
        # Simulate an exception during the request
        mock_get.side_effect = Exception("Network error")
        
        api_key = 'testapikey'
        start_station = 'Sydney Central'
        destination_station = 'Newcastle'
        departure_day = '20240507'
        departure_time = '1430'
        no_of_trips = 1

        # Print inputs
        print("test_get_train_info_exception:")
        print("Inputs:")
        print(f"  api_key: {api_key}")
        print(f"  start_station: {start_station}")
        print(f"  destination_station: {destination_station}")
        print(f"  departure_day: {departure_day}")
        print(f"  departure_time: {departure_time}")
        print(f"  no_of_trips: {no_of_trips}")

        train_info, trip_info_dict = get_train_info(api_key, start_station, destination_station, departure_day, departure_time, no_of_trips)

        # Print outputs
        print("Outputs:")
        print(f"  train_info: {train_info}")
        print(f"  trip_info_dict: {trip_info_dict}")

        try:
            self.assertEqual(len(train_info), 0)
            self.assertIsNone(trip_info_dict)
            print("  Result: Successful\n")
        except AssertionError as e:
            print(f"  Result: Unsuccessful - {str(e)}\n")

if __name__ == '__main__':
    unittest.main()
