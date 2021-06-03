from rest_framework.response import Response
import requests
from rest_framework import status
import os


def external_api_view(request, car_model, car_make):
    api_url = os.getenv("EXTERNAL_API_URL", "")
    if not (request.method == "POST" and api_url):
        return []

    api_url += f"/{car_make}?format=json"
    try:
        req = requests.request("GET", url=api_url)
    except requests.exceptions.RequestException as e:
        return Response(data={"error": f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if req.status_code != status.HTTP_200_OK:
        return Response(req.reason, status=req.status_code)
    resp = req.json()
    return [car for car in resp.get("Results") if car.get("Model_Name").lower() == car_model.lower()]
