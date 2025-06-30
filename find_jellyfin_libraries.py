#!/usr/bin/env python3
"""
Helper script to find Jellyfin library IDs for configuration.
Run this script to get the library IDs you need for the config.yml file.
"""

import requests
import yaml
from pathlib import Path

def get_jellyfin_libraries(url, api_key):
    """Get all libraries from Jellyfin"""
    headers = {
        'X-Emby-Token': api_key,
        'Content-Type': 'application/json'
    }
    
    # Get all libraries
    response = requests.get(f"{url}/Users/Items", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get libraries: {response.status_code}")

def main():
    print("Jellyfin Library Finder")
    print("=" * 50)
    
    # Get Jellyfin connection details
    url = input("Enter your Jellyfin URL (e.g., http://jellyfin:8096): ").strip()
    api_key = input("Enter your Jellyfin API key: ").strip()
    
    if not url or not api_key:
        print("Error: Both URL and API key are required.")
        return
    
    try:
        # Get libraries
        libraries_data = get_jellyfin_libraries(url, api_key)
        
        print("\nFound Libraries:")
        print("-" * 30)
        
        for item in libraries_data.get('Items', []):
            item_id = item.get('Id')
            name = item.get('Name', 'Unknown')
            item_type = item.get('CollectionType', 'Unknown')
            
            print(f"ID: {item_id}")
            print(f"Name: {name}")
            print(f"Type: {item_type}")
            print("-" * 30)
        
        print("\nCopy these IDs to your config.yml file in the libraries section.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nMake sure:")
        print("1. Your Jellyfin URL is correct")
        print("2. Your API key is valid")
        print("3. Your Jellyfin server is accessible")

if __name__ == "__main__":
    main() 