import requests

def fetch_bike_data():
    response = requests.get("http://fiets.openov.nl/locaties.json")
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch bike data")
        return None

def get_bike_availability():
    data = fetch_bike_data()

    output = ''

    for location in data['locaties'].values():
        bikes = location.get('extra', {}).get('rentalBikes', None)
        bikes = int(bikes) if bikes is not None else "Geen OV-fietsen beschikbaar"
        output += f"{location['description']}: {bikes}\n"
    
    return output
