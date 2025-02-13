from src import *
from api.core import *
from api.battle import *
import json
import sys
import pygame
import colorama
from colorama import Fore, Back, Style

def renderer(state):
    print("(f) Buy EXP ($4) | (d) Reroll ($2)")

def main():
    player_num = 8
    players = [Player(i, f"player_{i}") for i in range(player_num)]
    game = AutoBattlerGame(players=players, seed=42)
    register_unit(game, "data/unit.csv")
    # wrap(players[0])
    for i in range(player_num):
        refresh_shop(game, players[i])
        players[i].gold = 100
        purchase_unit(game, players[i], 0)
        bench_to_field(players[i], 0)
    running = True
    while running:
        # Event Handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    print(Fore.YELLOW + Back.WHITE + "- Reroll -" + Fore.RESET + Back.RESET)
                elif event.key == pygame.K_f:
                    print(Fore.BLUE + Back.WHITE + "- Buy EXP -"  + Fore.RESET + Back.RESET)
        # Mechanism


if __name__ == "__main__":
    colorama.init()
    pygame.init()
    screen_width = 640
    screen_height = 480
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("pyTFT")
    main()
    pygame.quit()