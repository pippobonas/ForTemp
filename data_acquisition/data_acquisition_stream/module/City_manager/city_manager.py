import json
import os
import asyncio
"""
This module provides classes to manage location data and perform operations such as loading from and saving to a JSON file.
Classes:
    LocationData: A class to represent the data of a specific location.
    LocationManager: A class to manage multiple locations, including loading from and saving to a JSON file.
Usage example:
    # Load locations from a JSON file
    # Add a new location
    # Find a location by name
    print(f"Found: {location}")
    # Remove a location by name
    # List all loaded locations
    # Save updated locations to a JSON file
"""

class LocationData:
    def __init__(self, name, country, latitude, longitude, altitude):
        """Initializes a new instance of the LocationData class."""
        self.name = name
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude

    def __repr__(self):
        """Representation of the data structure."""
        return f"LocationData ( {self.name.ljust(24)}, {self.country},\tlat:{self.latitude},\tlong:{self.longitude},\talt:{self.altitude} )"


class LocationManager:
    def __init__(self):
        """Initializes a new instance of the LocationManager class."""
        self.locations = []
        self.min_longitude = 0
        self.max_longitude = 0
        self.min_latitude = 0
        self.max_latitude = 0
        self.file_path = os.path.join("data", 'locations.json')
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
        self.load_from_json()
        self.update_bounds()

    
    def load_from_json(self):
        """Loads location data from a JSON file."""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                for entry in data:
                    location = LocationData(
                        entry.get('name'),
                        entry.get('country'),
                        entry.get('latitude'),
                        entry.get('longitude'),
                        entry.get('altitude')
                    )
                    self.locations.append(location)
        except FileNotFoundError:
            print(f"File {self.file_path} not found.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON file {self.file_path}.")

    def update_bounds(self):
        """Updates the minimum and maximum latitude and longitude values."""
        if len(self.locations) == 0:
            return
        self.min_longitude = min(loc.longitude for loc in self.locations)
        self.max_longitude = max(loc.longitude for loc in self.locations)
        self.min_latitude = min(loc.latitude for loc in self.locations)
        self.max_latitude = max(loc.latitude for loc in self.locations)

    def save_to_json(self):
        """Saves location data to a JSON file."""
        data = []
        for location in self.locations:
            data.append({
                'name': location.name,
                'country': location.country,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'altitude': location.altitude
            })
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError:
            print(f"Error saving to file {self.file_path}.")

    def add_location(self, name, country, latitude, longitude, altitude):
        """Adds a new location to the list."""
        new_location = LocationData(name, country, latitude, longitude, altitude)
        self.locations.append(new_location)

    def remove_location(self, name):
        """Removes a location from the list by name."""
        self.locations = [loc for loc in self.locations if loc.name != name]

    def find_location_by_name(self, name):
        """Finds a location by name."""
        for loc in self.locations:
            if loc.name == name:
                return loc
        return None

    def list_locations(self):
        """Prints all loaded locations."""
        for loc in self.locations:
            print(loc)
