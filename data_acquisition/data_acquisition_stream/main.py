"""
This module handles the data acquisition process for weather data, including adding and removing cities, 
starting the acquisition process, and simulating data sending to a server.
Functions:
    operation(cities, weather: OpenWeatherCurrentWeather, location: dict, server: smd):
        Acquire weather data for a specific location, process it, and send it to a server.
    start(cities, weather: OpenWeatherCurrentWeather, send_server: smd):
        Start the data acquisition process for the specified cities.
    add(geocoding: OpenWeatherGeocoding, alt: Open_elevation, cities: dict, name, country):
        Add a new city to the list of cities to acquire.
    show(cities):
        Show the list of cities to acquire and bounds.
    remove(cities, name):
        Remove a city from the list of cities to acquire.
    simulate(server: smd):
        Simulate the sending of data to the server.
    main():
        Main function to handle user input and start the appropriate process based on the input.
"""
import os
import sys
import asyncio
from module.City_manager import city_manager as city_manager
from module.request_manager.OpenWeatherAPI import OpenWeatherCurrentWeather, OpenWeatherGeocoding 
from module.request_manager.Open_elevation import Open_elevation 
from module.request_manager.SendMyData import SendMyData as smd
from module.utils.my_log import stdo

async def operation(cities, weather: OpenWeatherCurrentWeather, location: dict, server: smd):
    """Acquire weather data for a specific location, process it, and send it to a server."""
    stdo(f"Data acquisition for {location.name}")
    data = await weather.get_current_weather(
        latitude=location.latitude, 
        longitude=location.longitude
    )
    if data is not None:
        await server.send_normalized(data, city=location.name)
        


async def start(cities, weather: OpenWeatherCurrentWeather, send_server: smd):
    """Start the data acquisition process for the specified cities."""
    stdo("[START]->Initialize")
    n_cities = len(cities.locations) 
    if n_cities == 0:
        stdo("[START]->No cities to acquire data for.")
        return
    tasks = [operation(cities, weather, location, send_server) for location in cities.locations]
    await asyncio.gather(*tasks)

    stdo("[END]->Data acquisition process completed.")

async def add(geocoding: OpenWeatherGeocoding, alt: Open_elevation, cities: dict, name, country):
    """Add a new city to the list of cities to acquire."""
    pos = await geocoding.get_geolocation(name)

    latitude = pos[0]['lat']
    longitude = pos[0]['lon']
    altitude = await alt.get_elevation(latitude, longitude)
    cities.add_location(name, country, latitude, longitude, altitude)
    cities.save_to_json()
    stdo(f"[ADD]->The city {name} has been added to the list.")

def show(cities):
    """Show the list of cities to acquire and bounds."""
    cities.list_locations()
    print(f"Latitude bounds: {cities.min_latitude} to {cities.max_latitude}")
    print(f"Longitude bounds: {cities.min_longitude} to {cities.max_longitude}")
    print(f"Numbers of cities: {len(cities.locations)}")

def remove(cities, name):
    """Remove a city from the list of cities to acquire."""
    
    cities.remove_location(name)
    cities.save_to_json()
    print(f"The city {name} has been removed from the list.")

async def simulate(server: smd):
    """Simulate the sending of data to the server."""
    print("Simulating sending data to the server...")
    
    data = {"SIMULAZIONE": "SIMULAZIONE"}
    while True:
        stdo("[SIMULATE]->Sending data to the server")
        await server.send_log(data)
        stdo("[SIMULATE]->Data sent to the server")
        await asyncio.sleep(30)
        
async def main():
    async with OpenWeatherGeocoding(os.getenv("GEOCODING_URL"), os.getenv("KEY_OPENWEATHER")) as geocoding, \
               OpenWeatherCurrentWeather(os.getenv("CURRENT_WEATHER_URL"), os.getenv("KEY_OPENWEATHER")) as weather, \
               Open_elevation(os.getenv("ELEVATION_URL")) as alt, \
               smd(os.getenv("SEND_SERVER")) as logstash:
        
        cities = city_manager.LocationManager()

        argv_true = False
        while not argv_true:
            if len(sys.argv) <= 1:
                print("Choose an option:")
                print("1.\t Start:   \t run the data acquisition process")
                print("2.\t Add:     \t add a city to the list of cities to acquire")
                print("3.\t Remove:  \t remove a city from the list of cities to acquire")
                print("4.\t Show:    \t show the list of cities to acquire")
                print("5.\t Simulate:\t simulate the sending of data to the server")
                print("6.\t Exit:    \t exit the program")
                choice = input("Choice: ")
            else:
                choice = sys.argv[1]
                argv_true = True
            if choice == "1" or choice == "start":
                await start(cities, weather, logstash)
            elif choice == "2" or choice == "add":
                if len(sys.argv) > 2:
                    name = sys.argv[2]
                    if len(sys.argv) > 3:
                        country = sys.argv[3]
                    else:
                        country = input("Country name: ")
                else:
                    name = input("City name: ")
                    country = input("Country name: ")
                await add(geocoding, alt, cities, name, country)
            elif choice == "3" or choice == "remove":
                if len(sys.argv) >= 2:
                    name = sys.argv[2]
                else:
                    name = input("Name of the city to remove: ")
                remove(cities, name)
            elif choice == "4" or choice == "show":
                show(cities)
            elif choice == "5" or choice == "simulate":
                await simulate(logstash)
            elif choice == "6" or choice == "exit":
                print("Exiting the program.")
                break
            else:
                print("Invalid choice")
            
if __name__ == "__main__":
    asyncio.run(main())