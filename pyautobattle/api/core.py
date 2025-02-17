from src import *
import random
import numpy as np
import csv
import json
import copy

def print_obs(obs: dict):
    print(json.dumps(obs, indent=4, sort_keys=True))

def wrap(obj: Base):
    print_obs(obj.observe())

def logger(t: str):
    print(t)
            