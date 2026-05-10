from datetime import datetime, timedelta

import requests

weather_params = {
	"latitude": 52.52,
	"longitude": 13.41,
	"hourly": "temperature_2m",
}


def get_weather(latitude: float, longitude: float, time: datetime):
	"""
	Takes a pair of latitude, longitude and time and returns the temperature that is closest to the given time
	in the form like {'time': '2026-05-10T03:00', 'temperature': 30}
	"""

	weather_params = {
		'latitude': latitude,
		'longitude': longitude,
		'hourly': 'temperature_2m',
		'start_hour': time.strftime('%Y-%m-%d'),
		'end_hour': (time + timedelta(days=1)).strftime('%Y-%m-%d'),
		'timezone': time.tzname()
	}
	response = requests.get(
		'https://api.open-meteo.com/v1/forecast',
		params=weather_params
	)

	if response.ok:
		response = response.json()
		response = [
			{
				'time': time,
				'temperature': temperature
			}
			for time, temperature in zip(response['hourly']['time'], response['hourly']['temperature_2m'])
		]

		# return the response that is closest to time.
		return min(response, key=lambda e: abs(datetime.fromisoformat(e['time']) - time.replace(tzinfo=None)))

	return 'temperature not found'
