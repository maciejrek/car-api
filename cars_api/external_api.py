import os
from typing import List

import requests
from rest_framework import status
from rest_framework.request import Request


def external_api_call(request: Request, car_model: str, car_make: str) -> List:
    """Call to the external api.

    Args:
        request (Request): Request object
        car_model (str): Car model string
        car_make (str): Car make string

    Raises:
        AttributeError: An error occuring when incorrect request type and api url are provided
        RequestException: An error occuring during external api call
        ConnectionError: An error occuring if response code is other than 200
        ValueError: An error occuring if data specified by input parameters is not present in response

    Returns:
        List: List with data from external api, filtered by input parameters
    """
    api_url = os.getenv("EXTERNAL_API_URL", "")
    if not (request.method == "POST" and api_url):
        raise AttributeError("Wrong request method (post required) or missing api url env variable")

    api_url += f"/{car_make}?format=json"
    # requests.exceptions.RequestException can occure (should be handled by calling method)
    response = requests.get(url=api_url)
    if response.status_code != status.HTTP_200_OK:
        raise ConnectionError("External api error or API unavailable")
    resp = response.json()
    car = [car for car in resp.get("Results") if car.get("Model_Name").lower() == car_model.lower()]
    if not car:
        raise ValueError(f"No matching result in external api for {car_make} {car_model}")
    return car
