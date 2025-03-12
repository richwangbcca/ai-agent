import os
from collections import deque
from mistralai import Mistral
import discord
import logging
import json

import asyncio

import tools.gmaps as gmaps
import tools.eventmgmt as eventmgmt
from tools.gcal import GoogleCalendar

MISTRAL_MODEL = "mistral-large-latest"

PROMPT_1 = """
You are a helpful and friendly event planner. Keep the process concise but effective. 
Acknowledge and update any changes the user makes. Remind them of what they have planned so far every time a new detail is determined,
sharing the information in a readable and conversational format. When the user deems the event finalized, create a Google Calendar event
for them immediately. Do not share fields that have not been determined yet. Let the user know if there are any potential issues with the event, such 
as timing or an unreasonable budget. Prioritize the use of the search_maps tool for venue suggestions, and create the Google Calendar event 
as soon as everything is finalized without being prompted. When looking up suggestions, do not 

You assist with: 
- Theme & decorations
- Invitations & logistics
- Budget management

Tools:
- search_maps: Use Google Maps to find venues based on user requests. If a user requests venue suggestions, IMMEDIATELY call the search_maps
tool. Do NOT attempt to answer the request yourself. If no location is given, first ask for one, then call the tool. Do not tell the user to wait. Provide 
the Google Maps results immediately in your response. Share the venue name, address, and short description, ensuring that the provided information matches 
exactly the Google Maps results. 
- create_gcal_event: Once all details are confirmed, create and share an "add to calendar" link. Do not edit this link in any way when you share it
with the user. Do not tell them to wait. Provide the link immediately in your response in this format:
Here is your "add to calendar" link: [link]

Event Details:
If this is a new event, remind the user of your capabilities. Required fields: Title, Date, Time. These should be prioritized. Assist in filling in other 
details before finalizing the event. 
"""

PROMPT_2 = """
The following are the last 5 messages sent between you and the user.
"""


logger = logging.getLogger("discord")

class EventPlannerAgent:
    def __init__(self):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_maps",
                    "description": "Search Google Maps for venue locations based on conversation history",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "conversation_history": {
                                "type": "array",
                                "description": "Last five messages between the user and the bot",
                            }
                        },
                        "required": ["message"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "create_gcal_event",
                    "description": "Generate an \"add to calendar\" link to a Google Calendar event, given a title and a date and time",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the event"
                            },
                            "date": {
                                "type": "string",
                                "description": "The date of the event"
                            },
                            "time": {
                                "type": "string",
                                "description": "The time of the event"
                            },
                            "location": {
                                "type": "string",
                                "description": "The location of the event"
                            }
                        },
                        "required": ["title", "date", "time"]
                    }
                }
            }
        ]

        self.tools_to_functions = {
            "search_maps": self.search_maps,
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
        message_content = message.content
        prompt = PROMPT_1 + str(self.event_details) + PROMPT_2 + str(list(conversation_history))
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": message_content},
        ]

        tool_response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages,
            tools = self.tools,
            tool_choice = "auto"
        )

        if tool_response.choices[0].message.tool_calls:
            tool_calls = tool_response.choices[0].message.tool_calls
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_params = json.loads(tool_call.function.arguments)

                # Call the mapped function and account for default parameters
                function_result = self.tools_to_functions[function_name](**function_params)
                messages.append({"role": "user", "content": f"Result of {function_name}: {function_result}"})
        
        await asyncio.sleep(3)
        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages,
        )
        return response.choices[0].message.content
    
    def search_maps(self, conversation_history: list):
        logger.info("Running search_maps")
        query = gmaps.create_maps_query(conversation_history)
        results = gmaps.find_local_places(query)
        return results

    def create_gcal_event(self, title: str, date: str, time: str, location: str = ""):
        logger.info("Running create_gcal_event")
        gcal_details = {}
        gcal_details["title"] = title
        gcal_details["date"] = date
        gcal_details["time"] = time
        if location != "":
            gcal_details["location"] = location

        #gcal_client = GoogleCalendar()
        return ""#gcal_client.create_event(gcal_details)

