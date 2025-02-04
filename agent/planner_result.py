from typing import Optional, List, Any
from langchain_core.tools import tool
import requests

# @tool
def get_result(from_location: str, to_location: str) -> str:
    """Retrieve the plan result for a public transport journey from one location to another."""

    from_lat, from_lon = map(float, from_location.split(','))
    to_lat, to_lon = map(float, to_location.split(','))

    from_lat = 51.925452
    from_lon = 4.477096

    to_lat = 52.368625
    to_lon = 4.902534

    url = 'https://api.r-ov.nl/plan/v2'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        "arriveBy": False,
        "time": "12:30:00",
        "date": "2025-02-04",
        "departFromPlace": {
            "lat": from_lat,
            "lon": from_lon
        },
        "arriveAtPlace": {
            "lat": to_lat,
            "lon": to_lon
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        print("Error: ", response.text)
        return "Sorry, I couldn't find a route for that journey."
    
    responses = response.json()

    if not responses.get("itineraries"):
        return "Sorry, I couldn't find a route for that journey."
    
    itinerary = responses["itineraries"][0]
    transform_result(itinerary)
    return "Test"


def transform_result(itinerary) -> str:

    # From all legs remove the "legGeometry" and "intermediateStops" keys
    itinerary = remove_leg_geometry(itinerary)

    print(itinerary)

    # Remove all {, }, " and "
    itinerary = str(itinerary).replace("{", "").replace("}", "").replace('"', "").replace(",", "")

    print(itinerary)

    pass

def remove_leg_geometry(itinerary):
    # Each itinerary has a list of legs, each leg has a "legGeometry" key
    # Remove this key from each leg
    for leg in itinerary.get("legs", []):
        remove_intermediate_stops(leg)
        if "legGeometry" in leg:
            print("Removing legGeometry")
            del leg["legGeometry"]

    return itinerary

def remove_intermediate_stops(leg):
    # Each leg has a list of intermediate stops
    # Remove this key from each leg
    if "trip" in leg:
        trip = leg["trip"]
        if "trip" in trip:
            tripInfo = trip["trip"]
            if "stops" in tripInfo:
                print("Removing {} stops".format(len(tripInfo["stops"])))
                del tripInfo["stops"]
            if "trackMap" in tripInfo:
                print("Removing trackMap")
                del tripInfo["trackMap"]

    return leg

get_result("51.925452,4.477096", "52.368625,4.902534")
