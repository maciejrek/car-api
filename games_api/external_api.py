import os
from typing import List

import requests
from rest_framework import status
from rest_framework.request import Request


def external_api_call(request: Request, platform: str, name: str) -> List:
    """Call to the external api.

    Args:
        request (Request): Request object
        platform (str): Platform string
        name (str): Game name string

    Raises:
        AttributeError: An error occuring when incorrect request type and api url are provided
        RequestException: An error occuring during external api call
        ConnectionError: An error occuring if response code is other than 200
        ValueError: An error occuring if data specified by input parameters is not present in response

    Returns:
        List: List with data from external api, filtered by input parameters
    """
    api_url = os.getenv("BACKUP_EXTERNAL_API_URL", "")
    api_key = os.getenv("BACKUP_API_KEY", "")
    if not (request.method == "POST" and api_url and api_key):
        raise AttributeError("Wrong request method (post required), missing api key or missing api url env variable")

    api_url += f"/games?search={name}&page_size=1&key={api_key}"
    # requests.exceptions.RequestException can occure (should be handled by calling method)
    response = requests.get(url=api_url)
    if response.status_code != status.HTTP_200_OK:
        raise ConnectionError("External api error or API unavailable")
    resp = response.json()
    game = [
        game
        for game in resp.get("results")
        if game.get("platforms")[0].get("platform").get("name").lower() == platform.lower()
    ]

    if not game:
        raise ValueError(f"No matching result in external api for {name} {platform}")
    return game
