import os
from collections import deque
from mistralai import Mistral
import discord

import tools.gmaps as gmaps
import tools.eventmgmt as eventmgmt
from tools.gcal import GoogleCalendar

MISTRAL_MODEL = "mistral-large-latest"

PROMPT_1 = """
You are a helpful and friendly event planner. Keep the process concise but effective. 
Acknowledge and update any changes the user makes. Remind them of what they have planned so far if a reminder is not seen in the
conversation history, sharing the information in a readable and human-friendly
format. Let the user know if there are any potential issues with the event, such as timing or an unreasonable budget.

You assist with: 
- Theme & decorations
- Invitations & logistics
- Budget management

Tools:
- Venue search: Use Google Maps to find venues based on user requests. Do not provide venue suggestions yourself. Ask for a specific location before searching. Do
not respond to the user until the search is complete. Do not tell the user to wait. Provide the Google Maps results immediately in your response. Share the
venue name, address, and short description.
- Conversation scanner: Detects event details as they are decided.
- Google Calendar integration: Once all details are confirmed, create and share an "add to calendar" link. Do not edit this link in any way when you share it
with the user.

Event Details:
If this is a new event, remind the user of your capabilities. Required fields: Title, Date, Time. Assist in filling in other details before finalizing the event. 
"""

PROMPT_2 = """
The following are the last 5 messages sent between you and the user.
"""

class EventPlannerAgent:
    def __init__(self):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "find_local_places",
                    "description": "Search a query on Google Maps. Returns a dictionary that contains venue details",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The query to search on Google Maps",
                            }
                        },
                        "required": ["query"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "create_maps_query",
                    "description": "Generate a search query optimized for Google Maps",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message to generate a Google Maps query from"
                            }
                        },
                        "required": ["message"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "extract_event_data",
                    "description": "Automatically extract event data from conversation history and update the event details JSON",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "conversation_history": {
                                "type": "deque",
                                "description": "Contains the conversation history between the user and the bot"
                            },
                        }
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "create_gcal_event",
                    "description": "Generate an \"add to calendar\" link to a Google Calendar event, given a title and a date and time"
                }
            }
        ]
        self.tools_to_functions = {
            "find_local_places": gmaps.find_local_places,
            "create_maps_query": gmaps.create_maps_query,
            "extract_event_data": self.update_details,
            "create_gcal_event": self.create_gcal_event
        }

        self.event_details = {
        "title": "",
        "date": "",
        "time": "",
        "location": "",
        "theme": "",
        "invitation_details": {
            "visual_description": "",
            "blurb": ""
        },
        "guest_list": [],
        "expenses": {
            "total_budget": 0,
            "total_cost": 0,
            "food_and_drinks": {},
            "decorations": {},
            "logistics": {}
        },
        "other_details": []
        }

    async def run(self, message: discord.Message, conversation_history: deque):
        prompt = PROMPT_1 + str(self.event_details) + PROMPT_2 + str(list(conversation_history))
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": message.content},
        ]
        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages,
        )

        return response.choices[0].message.content
    
    def update_details(self, conversation_history: deque):
        updated_dict = eventmgmt.extract_event_data(conversation_history, self.event_details)
        self.event_details.update(updated_dict)

    def create_gcal_event(self):
        gcal_details = {}
        gcal_details["date"] = self.event_details["date"]
        gcal_details["time"] = self.event_details["time"]

        gcal_client = GoogleCalendar()
        return gcal_client.create_event(gcal_details)

