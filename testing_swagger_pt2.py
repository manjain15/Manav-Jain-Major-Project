from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint
from datetime import date, datetime

# Configure API key authorization: APIKey
configuration = swagger_client.Configuration()
configuration.api_key['Authorization'] = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJwMWpGZWhGZTB4cHJiT05OMWxsenBHYUN1UkNhN1VIMGxNNTl4UDZURkpzIiwiaWF0IjoxNzAzMTM4ODY4fQ.1pTAXxfPAJ64BzqxaRU9xnFPflsJ0niKPDC6BBmDpkk'
configuration.api_key_prefix['Authorization'] = 'apiKey'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
output_format = 'rapidJSON' # str | Used to set the response data type. This documentation only covers responses that use the JSON format. Setting the `outputFormat` value to `rapidJSON` is required to enable JSON output. 
name_sf = 'Circular Quay' # str | This is the search term that will be used to find locations. To lookup a coordinate, set `type_sf` to `coord`, and use the following format: `LONGITUDE:LATITUDE:EPSG:4326` (Note that longitude is first). For example, `151.206290:-33.884080:EPSG:4326`. To lookup a stop set `type_sf` to  `stop` and enter the stop id or global stop ID. For example, `10101100`  (default to Circular Quay)
coord_output_format = 'EPSG:4326' # str | This specifies the format the coordinates are returned in. While other variations are available, the `EPSG:4326` format will return the widely-used format.
type_sf = 'any' # str | This specifies the type of results expected in the list of returned stops. By specifying `any`, locations of all types can be returned. If you specifically know that you're searching using a coord, specify `coord`. Likewise, if you're using a stop ID or global stop ID as an input, use `stop` for more accurate results.  (optional)
tf_nswsf = 'true' # str | Including this parameter enables a number of options that result in the stop finder operating in the same way as the Transport for NSW Trip Planner web site.  (optional) (default to true)
version = '10.2.1.42' # str | Indicates which version of the API the caller is expecting for both request and response data. Note that if this version differs from the version listed above then the returned data may not be as expected.  (optional) (default to 10.2.1.42)

try:
    # Provides capability to return all NSW public transport stop, station, wharf, points of interest and known addresses to be used for auto-suggest/auto-complete (to be used with the Trip planner and Departure board APIs).
    api_response = api_instance.tfnsw_stopfinder_request(output_format, name_sf, coord_output_format, type_sf=type_sf, tf_nswsf=tf_nswsf, version=version)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->tfnsw_stopfinder_request: %s\n" % e)