import os
from mistralai import Mistral

def extract_event_data(conversation_history, event_details):
    """
    Extract event data from the conversation history between the bot and
    the user, and update the event_details accordingly.
    
    """
    token = os.getenv("MISTRAL_API_KEY")
    model = "mistral-large-latest"
    
    prompt = """
    You are an assistant helping to plan an event. 
    Here is the conversation history:
    """ + str(conversation_history) + """

    Please extract the following details from the conversation if they appear,
    and update the event_details JSON:
    - Title of the event 
    - Date of the event
    - Location of the event
    - Theme or description of the event
    - Invitation details
    - Expenses
    - Any other details (examples include alcohol-free, allergies, etc.)

    Ensure to return the updated event_details as a JSON-like structure.

    Current event_details:
    """ + str(event_details) + """

    Respond only with the updated event_details, nothing else.
    """

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

    updated_details = chat_response.choices[0].message.content
    return updated_details