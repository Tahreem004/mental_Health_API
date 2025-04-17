# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 17:05:25 2025

@author: tehre
"""

import requests

url = "http://localhost:5000/mental-health"
data = {
    "text": "میں بہت پریشان ہوں"
}

response = requests.post(url, json=data)
print(response.json())
