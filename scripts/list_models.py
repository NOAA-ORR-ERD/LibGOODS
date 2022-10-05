#!/usr/bin/env python

"""
list_models.py

microscript that list all the models' metadata currently active

and dumps it to a JSON file: all_models.json
"""

import json

from libgoods import api

data = api.list_models()

with open("all_models.json", "w", encoding="utf-8") as outfile:
    json.dump(data, outfile, indent=4)
