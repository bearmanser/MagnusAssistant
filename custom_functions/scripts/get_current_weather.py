import requests

from datetime import timedelta

from dateutil import parser





def get_current_weather(location, unit="celsius", datetime=None):

    if datetime:

        try:

            datetime = parser.parse(datetime)

        except ValueError as e:

            print(f"Failed to parse datetime: {e}")

            return



    coordinates = get_lat_lon(location)

    weather_data = get_weather(coordinates[0], coordinates[1], datetime)

    return {

        "location": location,

        "unit": unit,

        "datetime": datetime,

        "weather_data": weather_data,

    }





def get_lat_lon(place_name):

    url = "https://nominatim.openstreetmap.org/search"



    params = {"q": place_name, "format": "json", "limit": 1}



    headers = {"User-Agent": "MyApp/1.0 (https://myapp.com)"}



    response = requests.get(url, params=params, headers=headers)



    if response.status_code == 200:

        data = response.json()

        if data:

            latitude = data[0]["lat"]

            longitude = data[0]["lon"]

            return float(latitude), float(longitude)

        else:

            return f"Error: Could not find location for {place_name}"

    else:

        return (

            f"Error: Unable to fetch coordinates. Status Code: {response.status_code}"

        )





weather_code_map = {

    0: "Clear sky",

    1: "Mainly clear",

    2: "Partly cloudy",

    3: "Overcast",

    45: "Fog",

    48: "Depositing rime fog",

    51: "Drizzle: Light intensity",

    53: "Drizzle: Moderate intensity",

    55: "Drizzle: Dense intensity",

    56: "Freezing Drizzle: Light intensity",

    57: "Freezing Drizzle: Dense intensity",

    61: "Rain: Slight intensity",

    63: "Rain: Moderate intensity",

    65: "Rain: Heavy intensity",

    66: "Freezing Rain: Light intensity",

    67: "Freezing Rain: Heavy intensity",

    71: "Snow fall: Slight intensity",

    73: "Snow fall: Moderate intensity",

    75: "Snow fall: Heavy intensity",

    77: "Snow grains",

    80: "Rain showers: Slight intensity",

    81: "Rain showers: Moderate intensity",

    82: "Rain showers: Violent intensity",

    85: "Snow showers: Slight intensity",

    86: "Snow showers: Heavy intensity",

    95: "Thunderstorm: Slight or moderate",

    96: "Thunderstorm with slight hail",

    99: "Thunderstorm with heavy hail",

}





def get_weather(latitude, longitude, date=None):

    url = "https://api.open-meteo.com/v1/forecast"



    params = {

        "latitude": latitude,

        "longitude": longitude,

        "hourly": "temperature_2m,weathercode,windspeed_10m",

    }



    if date:

        if date.hour == 0 and date.minute == 0:

            date = date.replace(hour=13, minute=21)

        params["start_date"] = date.strftime("%Y-%m-%d")

        params["end_date"] = (date + timedelta(hours=1)).strftime("%Y-%m-%d")



    response = requests.get(url, params=params)



    if response.status_code == 200:

        data = response.json()



        weather = {

            "temperature": data["hourly"]["temperature_2m"][0],

            "windspeed": data["hourly"]["windspeed_10m"][0],

            "weather_description": weather_code_map.get(

                data["hourly"]["weathercode"][0], "Unknown weather"

            ),

        }

        return weather

    else:

        return (

            f"Error: Unable to fetch weather data. Status Code: {response.status_code}"

        )

