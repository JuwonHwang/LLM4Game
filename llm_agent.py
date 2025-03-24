import asyncio
import socketio
import json
import openai
import sys
from config.system_prompt import GAME_PROMPT, DIRECT_PROMPT, INTERNAL_COT, EXTERNAL_COT, HEAVY_COT_PROMPT
from config.tools import tool_rerole, tool_buy_exp, tool_buy_unit, tool_move_unit, tool_sell_unit, tool_none
from random_agent import RandomAgentClient
import os
from openai import RateLimitError

# Load server URL from a configuration file
def load_server_url(filename=".server"):
    try:
        with open(filename, "r") as file:
            return file.readline().strip()
    except FileNotFoundError:
        print("⚠ .server file not found. Using default URL.")
        return "http://localhost:5000"


MODEL = "gpt-4o"
SERVER_URL = load_server_url()

# Load OpenAI API key
def load_api():
    key = None
    with open("config/.api", mode="r") as f:
        key = f.read().strip('\n')
    assert key is not None
    openai.api_key = key
    return key

key = load_api()

class LLMAgentClient(RandomAgentClient):
    def __init__(self, user_id, server_url, prompt_type='direct'):
        super().__init__(user_id, server_url)
        
        if prompt_type == "direct":
            self.system_prompt = GAME_PROMPT + DIRECT_PROMPT
        elif prompt_type == "internal_cot":
            self.system_prompt = GAME_PROMPT + INTERNAL_COT
        elif prompt_type == "external_cot":
            self.system_prompt = GAME_PROMPT + EXTERNAL_COT
        else:
            self.system_prompt = GAME_PROMPT + DIRECT_PROMPT

        self.client = openai.AsyncOpenAI(api_key=key)
        self.answers = []

    def save_answers(self, game_id):
        os.makedirs(os.path.join("llm_output", game_id), exist_ok=True)
        with open(os.path.join("llm_output", f"{game_id}/{self.user_id}.json"), 'w', encoding='utf-8') as file:
            json.dump(self.answers, file, indent=4, ensure_ascii=False)

    async def get_action(self, actions, extra, game_state):
        """Uses LLM function calling to determine the best action based on the game state."""
        # 'buy_exp', 'buy_unit', 'reroll', 'sell_unit', 'move_unit', 'none'
        tools = [tool_none,]
        if "rerole" in actions:
            tools.append(tool_rerole)
        if "buy_exp" in actions:
            tools.append(tool_buy_exp)
        if "buy_unit" in actions:
            tools.append(tool_buy_unit)
        if "sell_unit" in actions:
            tools.append(tool_sell_unit)
        if "move_unit" in actions:
            tools.append(tool_move_unit)

        # Query OpenAI GPT model with function calling
        while True:
            try:
                response = await self.client.chat.completions.create(
                    model=MODEL,
                    store=False,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": "The latest round result: " + self.round_result_list[-1]},
                        {"role": "user", "content": "This is the current game state: " + json.dumps(game_state)},
                        {"role": "user", "content": "Unit Specs: " + json.dumps(self.unit_dict)},
                    ],
                    tools=tools,
                    max_tokens=400,
                )
                break
            except RateLimitError as e:
                print(f"{self.user_id}: Rate limit hit! Retrying in 3 seconds...")
                await asyncio.sleep(3)
        self.answers.append(response.choices[0].message.content)
        action_list = []
        try:
            if not response.choices[0].message.tool_calls:
                return action_list
            for tool_call in response.choices[0].message.tool_calls:
                action_data = tool_call.function
                if action_data:
                    action = action_data.name
                    action_args = json.loads(action_data.arguments)
                    self.answers.append([action, action_args])
                    if not action_args:
                        action_args = None
                    if action == "buy_unit":
                        action_args = action_args["shop_index"]
                    if action == "sell_unit":
                        action_args = (action_args["source_type"], action_args["source_index"])
                    if action == "move_unit":
                        action_args = (action_args["source_type"], action_args["target_type"], action_args["source_index"], action_args["target_index"])
                    action_list.append((action, action_args))
        except:
            pass
        return action_list

    async def step(self):
        await self.send_command('login', self.user_id)
        count = 0
        game_id = "unknown"
        while not self.end:
            if self.state['user'] and self.state['user']['game_id'] is None:
                await self.find_game()
            elif self.state['user'] and self.state['user']['game_id'] is not None:
                game_id = self.state['user']['game_id']
                break
            await asyncio.sleep(0.1)
        while not self.end:
            if self.state and self.state['user'] and self.state['user']['playing']:
                actions, extra = self.get_valid_actions(self.state['game']['player']['gold'], self.state['game'])
                if self.state["game"]["player"]["active"] and self.state['game']['player']['hp'] > 0:
                    action_list = await self.get_action(actions, extra, self.state["game"])
                    for action, params in action_list:
                        if action != "none":
                            await self.send_command(action, params)
                            await asyncio.sleep(0.1)
                    count += 1
            self.save_answers(game_id=game_id)
            await asyncio.sleep(2)
        await self.send_command("quit_game", None)
        await self.close()
        return

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python LLMAgent.py <user_id>")
        sys.exit(1)

    user_id = sys.argv[1]
    client = LLMAgentClient(user_id, SERVER_URL)

    loop = asyncio.get_event_loop()
    loop.create_task(client.connect_to_server())
    loop.run_forever()
