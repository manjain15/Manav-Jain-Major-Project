import unittest
from unittest.mock import patch, MagicMock
import zipfile
import io
import requests
from main import get_gtfs_data  # Adjust as needed

class TestGTFSData(unittest.TestCase):
    @patch('requests.get')
    def test_get_gtfs_data_success(self, mock_get):
        # Create an in-memory ZIP file with valid content
        zip_bytes = io.BytesIO()
        with zipfile.ZipFile(zip_bytes, 'w') as zf:
            zf.writestr('stops.txt', 'stop_id,stop_name\n1,Station1\n2,Station2')
        
        zip_bytes.seek(0)  # Reset the pointer to the beginning
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = zip_bytes.getvalue()  # The correct byte content
        mock_get.return_value = mock_response
        
        api_key = 'testapikey'
        api_url = 'http://example.com/gtfs'
        specific_file = None
        
        gtfs_data = get_gtfs_data(api_key, api_url, specific_file)
        
        self.assertIn('stops.txt', gtfs_data)
        self.assertTrue(gtfs_data['stops.txt'])

    @patch('requests.get')
    def test_get_gtfs_data_error(self, mock_get):
        # Mock a non-200 HTTP status to simulate an error condition
        mock_response = MagicMock()
        mock_response.status_code = 404  # Set to a non-200 status
        mock_response.content = b''  # Ensure it's a byte-like object
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        api_key = 'testapikey'
        api_url = 'http://example.com/gtfs'
        specific_file = None
        
        with self.assertRaises(requests.exceptions.HTTPError):
            get_gtfs_data(api_key, api_url, specific_file)

if __name__ == '__main__':
    unittest.main()
