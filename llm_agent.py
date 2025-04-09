import asyncio
import socketio
import json
import openai
import sys
from config.system_prompt import GAME_PROMPT, DIRECT_PROMPT, INTERNAL_COT, EXTERNAL_COT, SIMPLE_GAME_PROMPT
from config.actions import tool_rerole, tool_buy_exp, tool_buy_unit, tool_move_unit, tool_sell_unit, tool_none
from config.tools import tool_expected_gold, tool_field_strength, tool_unit_lookup
from random_agent import RandomAgentClient, load_server_url
import os
from openai import RateLimitError


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

API_KEY = load_api()

class LLMAgentClient(RandomAgentClient):
    def __init__(self, user_id, server_url, prompt_type='direct', message_limit=6):
        super().__init__(user_id, server_url)
        self.message_limit = message_limit
        
        self.system_prompt = GAME_PROMPT + json.dumps(self.unit_dict)
        if prompt_type == "direct":
            self.user_prompt = DIRECT_PROMPT
        elif prompt_type == "internal_cot":
            self.user_prompt = INTERNAL_COT
        elif prompt_type == "external_cot":
            self.user_prompt = EXTERNAL_COT
        else:
            self.user_prompt = DIRECT_PROMPT

        self.client = openai.AsyncOpenAI(api_key=API_KEY)
        self.answers = []
        self.tools = []

    def save_answers(self, game_id):
        os.makedirs(os.path.join("llm_output", game_id), exist_ok=True)
        with open(os.path.join("llm_output", f"{game_id}/{self.user_id}.json"), 'w', encoding='utf-8') as file:
            json.dump(self.messages, file, indent=4, ensure_ascii=False)

    async def get_action(self, game_state, result=None):
        actions = [tool_none, tool_rerole, tool_buy_exp, tool_buy_unit, tool_sell_unit, tool_move_unit]

        compact_game_state = {}
        compact_game_state["all_player_ids"] = list(game_state['game']['players'].keys())
        compact_game_state["player"] = game_state['player']

        def to_sparse(container, dim=1):
            sparse_container = {}
            for i, unit in enumerate(container):
                if unit:
                    sparse_container[f"{i}"] = unit
            return sparse_container
        
        compact_game_state["player"]['bench']['units'] = to_sparse(compact_game_state["player"]['bench']['units'])
        compact_game_state["player"]['shop']['units'] = to_sparse(compact_game_state["player"]['shop']['units'])
        compact_game_state['player']['field']['size'] = '28'
        compact_game_state["player"]['field']['units'] = to_sparse(compact_game_state["player"]['field']['units'])
        
        game_state_messages ={
            "role": "user",
            "content": json.dumps(compact_game_state)
        }
        self.messages.append(game_state_messages)
        self.messages.append({"role": "user", "content": self.user_prompt})

        if len(self.messages) > self.message_limit:
            input_messages = self.messages[-self.message_limit:]
        else:
            input_messages = self.messages
        
        while True:
            try:
                response = await self.client.chat.completions.create(
                    model=MODEL,
                    store=False,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                    ] + input_messages,
                    tools=actions + self.tools,
                )
                break
            except RateLimitError as e:
                print(f"{self.user_id}: Rate limit hit! Retrying in 1 seconds...")
                await asyncio.sleep(1)
        self.messages.append(
            {
                "role": "assistant",
                "content": f"{response.choices[0].message.content}"
            }
        )
        action_list = []
        try:
            if not response.choices[0].message.tool_calls:
                return action_list
            for tool_call in response.choices[0].message.tool_calls:
                action_data = tool_call.function
                if action_data:
                    action = action_data.name
                    action_args = json.loads(action_data.arguments)
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
            try:
                if self.state and self.state['user'] and self.state['user']['playing']:
                    if self.state["game"]["player"]["active"] and self.state['game']['player']['hp'] > 0:
                        action_list = await self.get_action(self.state["game"])
                        for action, params in action_list:
                            self.messages.append({
                                "role": "assistant",
                                "content": f"tool name: {action}" + (f" arguments: {params}" if params else "")
                            })
                            if action != "none":
                                await self.send_command(action, params)
                                await asyncio.sleep(0.1)
                        count += 1
            except:
                break
            self.save_answers(game_id=game_id)
            await asyncio.sleep(1)
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
