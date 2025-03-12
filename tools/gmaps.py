import os
import time
import requests
from mistralai import Mistral

TOKEN = os.getenv("MISTRAL_API_KEY")
MODEL = "mistral-large-latest"

def create_maps_query(conversation_history): 
    """
    Given a user's message, use Mistral AI to generate a Google Maps-optimized
    search query that aligns with what the user is looking for.
    params:
        - message (str): the message to generate a query from
    returns:
        - str: the optimized Google Maps query
    """
    
    prompt = """
    Given this message, generate a search query that can be
    used to search Google Maps for results. Provide a short answer
    that contains only the search query. If the message is not relevant
    to searching for a venue, return an empty string.

    Example:
    Message: I'm looking for restaurants near Stanford University
    Response: Restaurants near Stanford University

    Message: I want to find somewhere to hold a kids birthday party in San Francisco
    Response: Kids birthday party venues in San Francisco

    Here is the message:
    """ + str(conversation_history)
    time.sleep(1)

    client = Mistral(api_key=TOKEN)
    chat_response = client.chat.complete(
        model = MODEL,
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return chat_response.choices[0].message.content



def find_local_places(query):
    """
    Use Google Maps API to search a text query. This query should be AI generated given the
    user's request.
    params:
        - query (str): The text query to search Google Maps with
    return:
        - TODO Need to make this a good return type that will work well with Mistral
    """
    token = os.getenv('GOOGLE_TOKEN')

    textsearch_url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": token,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.googleMapsLinks"
    }

    text_query = {"textQuery": query}
    
    response = requests.post(textsearch_url, headers=headers, json=text_query)
    return_string = ""
    if response.status_code == 200:
        data = response.json()
        
        # Check if there are results
        if 'places' in data:
            print(str(len(data['places'])) + " results found")
            for place in data['places']:
                name = place.get('displayName', {}).get('text', 'No name available')
                address = place.get('formattedAddress', 'No address found')
                link = place.get('googleMapsLinks', {}).get('placeUri', 'about:blank')
                return_string += f"Restaurant: {name}\nAddress: {address}\nLink: {link}\n\n"
        else:
            return "I wasn't able to find any venues nearby. Do you have another query in mind?"
    else:
        return "Seems like I can't look up what's nearby (Error {response.status_code}). Let's revisit this later."
    
    print(return_string)
    return return_string