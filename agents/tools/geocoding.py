import requests


def geocoding(city: str) -> dict:
    """
    Accepts city param and returns a pair of latitude, longitude coordinates where the city is.
    If nothing is found it returns a simple message saying so.
    """

    response = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": city, "format": "json", "limit": 1},
        headers={"User-Agent": "my-app/1.0"}
    )

    if response.ok:
        response = response.json()
        return {
            'latitude': response[0]['lat'],
            'longitude': response[0]['lon']
        }
    return {'message': 'city not found'}