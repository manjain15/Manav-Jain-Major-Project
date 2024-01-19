from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: APIKey
configuration = swagger_client.Configuration()
configuration.api_key['Authorization'] = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJwMWpGZWhGZTB4cHJiT05OMWxsenBHYUN1UkNhN1VIMGxNNTl4UDZURkpzIiwiaWF0IjoxNzAzMTM4ODY4fQ.1pTAXxfPAJ64BzqxaRU9xnFPflsJ0niKPDC6BBmDpkk'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
configuration.api_key_prefix['Authorization'] = 'apiKey'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
output_format = 'rapidJSON' # str | Used to set the response data type. This documentation only covers responses that use the JSON format. Setting the `outputFormat` value to `rapidJSON` is required to enable JSON output. 
coord_output_format = 'EPSG:4326' # str | This specifies the format the coordinates are returned in. While other variations are available, the `EPSG:4326` format will return the widely-used format.
type_dm = 'stop' # str | This specifies the type of results expected based on the search input in `name_dm`. By specifying `any`, locations of all types can be returned. Typically, this API call is used for a specific stop, so `stop` should be used along with a stop ID or global stop ID in `name_dm`.  (default to stop)
name_dm = '10111010' # str | This is the search term that will be used to find locations. If the combination of this value and `type_dm` results in more than one location found - or `mode` is not set to `direct`, then a list of stops and no departures will be returned. If `type_dm` is set to `stop` then this value can take a stop ID or a global stop ID.  (default to 10111010)
mode = 'direct' # str | This allows the departure board to display directly without going through the stop verification process. Use this when the stop is known. This relies on the given combination of `type_dm` and `name_dm` returning only a single result, otherwise a list of stops and no departures shall be returned.  (optional) (default to direct)
#name_key_dm = '$USEPOINT$' # str | Setting this parameter to `$USEPOINT$` enables you to request departures for a specific platform within a station. If this isn't used, then departures for all platforms at the stop specified in `name_dm` are returned.  (optional)
itd_date = '20240119' # str | The reference date used when searching trips, in `YYYYMMDD` format. For instance, 20160901 refers to 1 September 2016. Works in conjunction with the `itdTime` value. If not specified, the current server date is used.  (optional) (default to 20161001)
itd_time = '2353' # str | The reference time used when searching trips, in `HHMM` 24-hour format. For instance, 2215 refers to 10:15 PM. | Works in conjunction with the `itdDate` value. If not specified, the current server time is used.  (optional) (default to 1200)
departure_monitor_macro = 'true' # str | Including this parameter enables a number of options that result in the departure monitor operating in the same way as the Transport for NSW Trip Planner web site. It is recommended this is enabled, along with the `TfNSWDM` parameter.  (optional) (default to true)
# excluded_means = 'excluded_means_example' # str | This parameter which means of transport to exclude from the departure monitor. To exclude one means, select one of the following: `1` = train, `2` = metro, `4` = light rail, `5` = bus, `7` = coach, `9` = ferry, `11` = school bus. `checkbox` allows you to exclude more than one means of transport when used in conjunction with the `exclMOT_<ID>` parameters.  (optional)
# excl_mot_1 = 'excl_mot_1_example' # str | Excludes train services from the departure monitor.  Must be used in conjunction with `excludedMeans=checkbox`  (optional)
# excl_mot_2 = 'excl_mot_2_example' # str | Excludes metro services from the departure monitor.  Must be used in conjunction with `excludedMeans=checkbox`  (optional)
# excl_mot_4 = 'excl_mot_4_example' # str | Excludes light rail services from the departure monitor.  Must be used in conjunction with `excludedMeans=checkbox`  (optional)
# excl_mot_5 = 'excl_mot_5_example' # str | Excludes bus services from the departure monitor.  Must be used in conjunction with `excludedMeans=checkbox`  (optional)
# excl_mot_7 = 'excl_mot_7_example' # str | Excludes coach services from the departure monitor.  Must be used in conjunction with `excludedMeans=checkbox`  (optional)
# excl_mot_9 = 'excl_mot_9_example' # str | Excludes ferry services from the departure monitor.  Must be used in conjunction with `excludedMeans=checkbox`  (optional)
# excl_mot_11 = 'excl_mot_11_example' # str | Excludes school bus services from the departure monitor.  Must be used in conjunction with `excludedMeans=checkbox`  (optional)
tf_nswdm = 'true' # str | Including this parameter enables a number of options that result in the departure monitor operating in the same way as the Transport for NSW Trip Planner web site, including enabling real-time data. It is recommended this is enabled, along with the `departureMonitorMacro` parameter.  (optional) (default to true)
version = '10.2.1.42' # str | Indicates which version of the API the caller is expecting for both request and response data. Note that if this version differs from the version listed above then the returned data may not be as expected.  (optional) (default to 10.2.1.42)

try:
    # Provides capability to provide NSW public transport departure information from a stop, station or wharf including real-time.
    api_response = api_instance.tfnsw_dm_request(output_format, coord_output_format, type_dm, name_dm, mode=mode, itd_date=itd_date, itd_time=itd_time, departure_monitor_macro=departure_monitor_macro, tf_nswdm=tf_nswdm, version=version)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->tfnsw_dm_request: %s\n" % e)