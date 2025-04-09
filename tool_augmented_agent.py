import asyncio
import json
import sys
from config.system_prompt import GAME_PROMPT
from config.actions import tool_rerole, tool_buy_exp, tool_buy_unit, tool_move_unit, tool_sell_unit, tool_none
from config.tools import tool_expected_gold, tool_field_strength, tool_unit_lookup
from llm_agent import LLMAgentClient, load_server_url, load_api
from pyautobattle.src.util import get_price
from openai import RateLimitError

MODEL = "gpt-4o"
SERVER_URL = load_server_url()
API_KEY = load_api()

class ToolAugmentedLLMAgentClient(LLMAgentClient):
    def __init__(self, user_id, server_url, prompt_type='direct'):
        super().__init__(user_id, server_url, prompt_type)
        self.system_prompt = GAME_PROMPT
        self.tools = [tool_field_strength, tool_expected_gold, tool_unit_lookup]

    def call_external_tool(self, action, params):
        func = getattr(self, action, None)
        if func:
            print('external: ', action, params)
            if params:
                result = func(params)
            else:
                result = func()
            print(f"{action}, {params}, {result}")
            return {
                "role": "assistant",
                "content": f"{result}"
            }
        else:
            return None
        
    def view_unit_status(self, params):
        return self.unit_dict.get(params.get('unit_id'))
    
    def calculate_next_round_expected_gold(self):
        turn_gold = 10
        interest = min(int(self.state.get('game').get('player').get('gold')) % 10, 5)
        return turn_gold + interest
    
    def calculate_field_strength_by_player_id(self, player_id):
        player_field = self.state.get('game').get('game').get('players').get(player_id.get('player_id')).get('field').get('units')
        total_price = 0
        for unit in player_field:
            if unit:
                total_price += get_price(unit)
        return total_price
        
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
                                "content": f"tool name: {action}" + (f", arguments: {params}" if params is not None else "")
                            })
                            if action in [tool['function']['name'] for tool in self.tools]:
                                tool_result = self.call_external_tool(action, params)
                                if tool_result:
                                    self.messages.append(tool_result)
                            elif action != "none":
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
