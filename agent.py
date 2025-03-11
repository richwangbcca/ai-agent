import os
from collections import deque
from mistralai import Mistral
import discord

import tools.gmaps as gmaps
import tools.eventmgmt as eventmgmt

MISTRAL_MODEL = "mistral-large-latest"

PROMPT_1 = """
You are a helpful and friendly event planner. 
You will keep the process concise but effective. Be sure to acknowledge any changes that the user makes to the event,
and update the event accordingly. Every once in a while, remind the user what they have planned already.
You will help them plan the theme, design invitations, manage budgets, organize logistics, and plan decorations. 
If the user asks for suggestions, you may provide them, but keep the conversation focused on planning the overall event.
You have tools that help to search Google Maps for locations. Use the tool if the user asks for venue suggestions, and do
not provide your own suggestions. Immediately return results from the tool. Make sure to ask for a specific location for a
venue; do not assume their general location.

Example:
User: "I want to plan a birthday dinner. Can you provide some restaurant suggestions near Stanford University?"
Response: "Here are some restaurant suggestions near Stanford University: [INSERT GOOGLE MAPS RESULTS]"

You have another tool that scans the conversation history to identify event details to update the event with. Use this tool whenever an
event detail is decided upon.

The following is the previously decided upon entries of the event. You should ultimately address and fill in all of these fields before 
summarizing and creating the event. If all fields are empty, then this is a new event and no details have been decided upon.
"""

PROMPT_2 = """
The following are the last ten messages sent by the user.
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
            }
        ]
        self.tools_to_functions = {
            "find_local_places": gmaps.find_local_places,
            "create_maps_query": gmaps.create_maps_query,
            "extract_event_data": self.update_details
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

