import json
import os
from argparse import ArgumentParser
from datetime import datetime

from anthropic import Anthropic, beta_tool
from dotenv import load_dotenv

from agents.tools.geocoding import geocoding
from agents.tools.time import get_current_local_time
from agents.tools.weather import get_weather

load_dotenv('.env')
load_dotenv('.env.local')

time_format = '%Y-%m-%dT%H:%M:%S%z'


def call_tool(tool_name: str, tool_input: dict):
    """
    Interface between tools and LLM.
    It transforms input arguments in the way functions need
    and formats output in the way LLMs need
    """
    if tool_name == 'get_weather':
        tool_input['time'] = datetime.strptime(tool_input['time'], time_format)
        return get_weather(**tool_input)
    if tool_name == 'geocoding':
        return geocoding(**tool_input)
    if tool_name == 'get_current_local_time':
        current_local_time = get_current_local_time()
        return current_local_time.strftime(time_format)
    return 'tool not found'


def main():
    """
    Running with different questions

    What is the weather in Syntagma square now?         - Success
    What is the weather in Syntagma square tomorrow?    - Success
    What is the weather in Syntagma square in one year? - Fail

    """
    argument_parser = ArgumentParser()
    argument_parser.add_argument('--message', default='What is the weather in Syntagma square now? Give also the coordinates of this spot in the form lat,long')

    args = argument_parser.parse_args()

    tools = [
        beta_tool(get_weather), beta_tool(geocoding), beta_tool(get_current_local_time)
    ]

    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    messages = [
        {'role': 'user',
         'content': args.message}
    ]

    response = client.messages.create(
        model='claude-sonnet-4-5',
        max_tokens=1024,
        messages=messages,
        tools=[x.to_dict() for x in tools]
    )
    print(response.content)
    while response.stop_reason == 'tool_use':

        tool_uses = []
        for block in response.content:
            if block.type == 'tool_use':
                tool_output = call_tool(block.name, block.input)
                print(f'called tool {block.name}'
                      f'\n\t input {block.input}'
                      f'\n\t output: {tool_output}')
                tool_uses.append(
                    {
                        'type': 'tool_result',
                        'tool_use_id': block.id,
                        'content': json.dumps(tool_output)
                    }
                )

        messages.append({'role': 'assistant', 'content': response.content})
        messages.append({'role': 'user', 'content': tool_uses})
        response = client.messages.create(
            model='claude-sonnet-4-5',
            max_tokens=1024,
            messages=messages,
            tools=[x.to_dict() for x in tools]
        )
    for content in response.content:
        if content.type == 'text':
            print(content.text)


if __name__ == '__main__':

    main()