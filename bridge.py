import requests
import json
import  os

from dotenv import load_dotenv

load_dotenv()

URL = os.environ.get("FRONTEND_URL")

def get_endpoint_with_data(endpoint, **kwargs):
    url = URL + endpoint[0] + "/"
    headers = {"Content-Type": "application/json"}

    data = kwargs
    print(data)
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(response.json())
        response.raise_for_status()  # Raise an exception for bad status codes
        return (response.json())
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        print(f"Raw response text: {response.text}")


def call_endpoint_with_params(endpoint, **kwargs):

    url = URL + endpoint[0] + "/"
    params = kwargs

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        print(f"Raw response text: {response.text}")