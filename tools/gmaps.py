import os
import requests

token = os.getenv('GOOGLE_TOKEN')

def find_local_places(query):
    """
    Use Google Maps API to search a text query. This query should be AI generated given the
    user's request.
    params:
        - query (str): The text query to search Google Maps with
    return:
        - TODO Need to make this a good return type that will work well with Mistral
    """
    textsearch_url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": token,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.googleMapsLinks"
    }

    text_query = {"textQuery": query}
    
    response = requests.post(textsearch_url, headers=headers, json=text_query)

    if response.status_code == 200:
        data = response.json()
        
        # Check if there are results
        if 'places' in data:
            print(str(len(data['places'])) + " results found")
            for place in data['places']:
                name = place.get('displayName', {}).get('text', 'No name available')
                address = place.get('formattedAddress', 'No address found')
                maps_link = place.get('googleMapsLinks', {}).get('placeUri', 'about:blank')
                print(f"Restaurant: {name}\nAddress: {address}\nLink: {maps_link}\n")
        else:
            print("I wasn't able to find any venues nearby. Do you have another query in mind?")
    else:
        print(f"Seems like I can't look up what's nearby (Error {response.status_code}). Let's revisit this later.")
    

find_local_places('Birthday party venue near Stanford University')