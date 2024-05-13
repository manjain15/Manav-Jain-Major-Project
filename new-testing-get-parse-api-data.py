import unittest
from unittest.mock import MagicMock, patch
from main import get_gtfs_data, parse_gtfs_data
import json

# Load the API key from a JSON file
with open('api_key.json') as f:
        api_key_file = json.load(f)
api_key = api_key_file['API_KEY']

class TestGTFSFunctions(unittest.TestCase):
    
    @patch('main.requests.get')
    @patch('main.zipfile.ZipFile')
    def test_get_gtfs_data_positive(self, mock_zipfile, mock_get):
        api_url = "https://api.transport.nsw.gov.au/v1/gtfs/schedule/buses"
        specific_file = "stops.txt"
        
        expected_content = b'content_of_specific_file'
        
        # Mocking the response of requests.get()
        mock_get.return_value.content = expected_content
        mock_get.return_value.raise_for_status.return_value = None
        
        # Mocking the ZipFile object
        mock_zipfile_instance = MagicMock()
        mock_zipfile_instance.__enter__.return_value.read.return_value = expected_content
        mock_zipfile.return_value = mock_zipfile_instance
        
        # Call the function
        result = get_gtfs_data(api_key, api_url, specific_file)
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertIn(specific_file, result)
        self.assertEqual(result[specific_file], expected_content.decode("utf-8"))
        
    def test_get_gtfs_data_negative(self):
        # Test with invalid API key
        with self.assertRaises(Exception):
            get_gtfs_data(api_key=None, api_url="https://api.transport.nsw.gov.au/v1/gtfs/schedule/buses", specific_file="stops.txt")
        
        # Test with invalid API URL
        with self.assertRaises(Exception):
            get_gtfs_data(api_key=api_key, api_url=None, specific_file="stops.txt")
        
        # Test with non-200 status code
        with patch('main.requests.get') as mock_get:
            mock_get.return_value.raise_for_status.side_effect = Exception("Non-200 status code")
            with self.assertRaises(Exception):
                get_gtfs_data(api_key=api_key, api_url="https://api.transport.nsw.gov.au/v1/gtfs/schedule/buses", specific_file="stops.txt")
    
    def test_parse_gtfs_data(self):
        # Test with valid data
        data = {
            'file1.txt': 'id,name\n1,John\n2,Doe\n',
            'file2.txt': 'id,age\n1,30\n2,25\n'
        }
        specific_file = 'file1.txt'
        
        expected_parsed_data = {
            'file1.txt': [{'id': '1', 'name': 'John'}, {'id': '2', 'name': 'Doe'}]
        }
        
        result = parse_gtfs_data(data, specific_file)
        self.assertEqual(result, expected_parsed_data)
        
        # Test with invalid data
        result = parse_gtfs_data(None, specific_file)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
