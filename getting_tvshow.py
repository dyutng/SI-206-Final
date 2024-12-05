import requests
import json
import unittest
import os

## for tvdb
API_KEY = '04e07cae-60ca-4d40-ba16-6de5031dc5e1'

def get_json_content(filename):
    '''
    ARGUMENTS: 
        filename: name of file to be opened

    RETURNS: 
        json dictionary OR an empty dict if the file could not be opened 
    '''
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}