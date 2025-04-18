import requests
import json

URL = "https://investment-analyzer-fastapi-5e7e9fc21917.herokuapp.com/"
#URL = "http://127.0.0.1:8000/"

def get_endpoint_with_data(endpoint, **kwargs):
    url = URL + endpoint[0] + "/"
    headers = {"Content-Type": "application/json"}

    data = kwargs
    print(data)
    try:
        response = requests.get(url, headers=headers, data=json.dumps(data))
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