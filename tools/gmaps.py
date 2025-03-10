import os
import requests
from mistralai import Mistral

def create_maps_query(message): 
    """
    Given a user's message, use Mistral AI to generate a Google Maps-optimized
    search query that aligns with what the user is looking for.
    params:
        - message (str): the message to generate a query from
    returns:
        - str: the optimized Google Maps query
    """
    token = os.getenv("MISTRAL_API_KEY")
    model = "mistral-large-latest"
    
    prompt = """
    Given this message, generate a search query that can be
    used to search Google Maps for results. Provide a short answer
    that contains only the search query.

    Example:
    Message: I'm looking for restaurants near Stanford University
    Response: Restaurants near Stanford University

    Message: I want to find somewhere to hold a kids birthday party in San Francisco
    Response: Kids birthday party venues in San Francisco

    Here is the message:
    """ + message

    client = Mistral(api_key=token)
    chat_response = client.chat.complete(
        model = model,
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
    


query = create_maps_query("I want to hold a birthday dinner in downtown Palo Alto")
print(query)
find_local_places(query)