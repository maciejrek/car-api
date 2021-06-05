from collections import OrderedDict

import pytest
from pytest_mock import MockerFixture
from requests.exceptions import RequestException
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIRequestFactory

from cars_api.external_api import external_api_call
from cars_api.models import Car, Rate

"""######### AUX #########"""


def add_marks(*args):  # type: ignore
    """Add multiple marks to test."""

    def _(f):  # type: ignore
        for mark in args:
            f = getattr(pytest.mark, mark)(f)
        return f

    return _


class MockResponse:
    """Mock response object in external_api tests."""

    def __init__(self, json_data, status_code, url=""):
        """Init method of MockResponse class.

        Args:
            json_data: Mocked data
            status_code: Mocked status code
            url: mocked url..
        """
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        """Return mocked data.

        Returns:
            Dict: return mocked data as dict.
        """
        return self.json_data


@pytest.fixture(scope="function")
def positive_response_from_external_api(mocker: MockerFixture):
    mocker.patch(
        "cars_api.views.external_api_call",
        return_value={
            "Count": 3,
            "Message": "Response returned successfully",
            "SearchCriteria": "Make:honda",
            "Results": [
                {"Make_ID": 474, "Make_Name": "HONDA", "Model_ID": 1861, "Model_Name": "Accord"},
                {"Make_ID": 474, "Make_Name": "HONDA", "Model_ID": 1863, "Model_Name": "Civic"},
                {"Make_ID": 474, "Make_Name": "HONDA", "Model_ID": 1864, "Model_Name": "Pilot"},
            ],
        },
    )


@pytest.fixture(scope="function")
def db_with_multiple_car_records(db):
    Car.objects.create(model="Honda", make="Accord")
    Car.objects.create(model="Honda", make="Civic")
    Car.objects.create(model="Honda", make="Pilot")


@pytest.fixture(scope="function")
def db_with_multiple_car_and_rating_records(db):
    car1 = Car.objects.create(model="Honda", make="Accord")
    car2 = Car.objects.create(model="Honda", make="Civic")
    car3 = Car.objects.create(model="Honda", make="Pilot")
    Rate.objects.create(car_id=car1, rating=1)
    Rate.objects.create(car_id=car2, rating=2)
    Rate.objects.create(car_id=car2, rating=3)
    Rate.objects.create(car_id=car3, rating=4)
    Rate.objects.create(car_id=car3, rating=4)
    Rate.objects.create(car_id=car3, rating=5)


@pytest.fixture(scope="function")
def db_with_single_car_record(db):
    Car.objects.create(model="Honda", make="Civic")


def mock_external_api_call_raise_value_error(request, car_model, car_make):
    raise ValueError(f"No matching result in external api for {car_make} {car_model}")


def mock_external_api_call_raise_connection_error(request, car_model, car_make):
    raise ConnectionError("External api error or API unavailable")


def mock_external_api_call_raise_attribute_error(request, car_model, car_make):
    raise AttributeError("Wrong request method (post required) or missing api url env variable")


def mock_external_api_call_raise_request_exception(request, car_model, car_make):
    raise RequestException("")


"""######### Views Tests #########"""


@add_marks("positive_case", "post", "cars_endpoint")
@pytest.mark.django_db(reset_sequences=True)
def test_post_cars_endpoint_positive_case_create_two_car_records(positive_response_from_external_api, client):
    # create first car
    car_make = "Honda"
    car_model = "Pilot"
    expected_response = {"make": car_make, "model": car_model}
    response = client.post("/cars/", {"make": {car_make}, "model": {car_model}})
    # validate results
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_response
    assert len(Car.objects.all()) == 1
    # create second car
    car_make = "Honda"
    car_model = "Civic"
    expected_response = {"make": car_make, "model": car_model}
    response = client.post("/cars/", {"make": {car_make}, "model": {car_model}})
    # validate results
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_response
    assert len(Car.objects.all()) == 2


@add_marks("negative_case", "post", "cars_endpoint")
@pytest.mark.django_db(reset_sequences=True)
def test_post_cars_endpoint_negative_case_duplicate_car_records(positive_response_from_external_api, client):
    # create car
    car_make = "Honda"
    car_model = "Pilot"
    expected_response = {"make": car_make, "model": car_model}
    response = client.post("/cars/", {"make": {car_make}, "model": {car_model}})
    # validate results
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_response
    assert len(Car.objects.all()) == 1
    # create duplicate car
    car_make = "Honda"
    car_model = "Pilot"
    expected_response = {"non_field_errors": ["The fields make, model must make a unique set."]}
    response = client.post("/cars/", {"make": {car_make}, "model": {car_model}})
    # validate results
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == expected_response
    assert len(Car.objects.all()) == 1


@add_marks("negative_case", "post", "cars_endpoint")
@pytest.mark.django_db(reset_sequences=True)
def test_post_cars_endpoint_negative_case_missing_model(positive_response_from_external_api, client):
    # create car with missing field
    expected_response = {"model": ["This field is required."]}
    car_make = "Honda"
    response = client.post("/cars/", {"make": {car_make}})
    # validate results
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == expected_response
    assert len(Car.objects.all()) == 0


@add_marks("negative_case", "post", "cars_endpoint")
@pytest.mark.django_db(reset_sequences=True)
def test_post_cars_endpoint_negative_case_missing_make(positive_response_from_external_api, client):
    # create car with missing field
    car_model = "Pilot"
    expected_response = {"make": ["This field is required."]}
    response = client.post("/cars/", {"model": {car_model}})
    # validate results
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == expected_response
    assert len(Car.objects.all()) == 0


@add_marks("negative_case", "post", "cars_endpoint", "external_api")
@pytest.mark.django_db(reset_sequences=True)
def test_post_cars_endpoint_negative_case_no_matching_results_from_external_api(mocker, client):
    mocker.patch("cars_api.views.external_api_call", new=mock_external_api_call_raise_value_error)
    # create car with mocked response from external api
    car_make = "Honda"
    car_model = "Civic"
    expected_response = {"external_api_error": f"No matching result in external api for {car_make} {car_model}"}
    response = client.post("/cars/", {"make": {car_make}, "model": {car_model}})
    # validate results
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data == expected_response
    assert len(Car.objects.all()) == 0


@add_marks("negative_case", "post", "cars_endpoint", "external_api")
@pytest.mark.django_db(reset_sequences=True)
def test_post_cars_endpoint_negative_case_incorrect_request_type_or_no_api_url(mocker, client):
    mocker.patch("cars_api.views.external_api_call", new=mock_external_api_call_raise_attribute_error)
    # create car with mocked response from external api
    car_make = "Honda"
    car_model = "Civic"
    expected_response = {"external_api_error": "Wrong request method (post required) or missing api url env variable"}
    response = client.post("/cars/", {"make": {car_make}, "model": {car_model}})
    # validate results
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == expected_response
    assert len(Car.objects.all()) == 0


@add_marks("negative_case", "post", "cars_endpoint", "external_api")
@pytest.mark.django_db(reset_sequences=True)
def test_post_cars_endpoint_negative_case_response_code_other_than_200(mocker, client):
    mocker.patch("cars_api.views.external_api_call", new=mock_external_api_call_raise_connection_error)
    # create car with mocked response from external api
    car_make = "Honda"
    car_model = "Civic"
    expected_response = {"external_api_error": "External api error or API unavailable"}
    response = client.post("/cars/", {"make": {car_make}, "model": {car_model}})
    # validate results
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == expected_response
    assert len(Car.objects.all()) == 0


@add_marks("negative_case", "post", "cars_endpoint", "external_api")
@pytest.mark.django_db(reset_sequences=True)
def test_post_cars_endpoint_negative_case_external_request_exception(mocker, client):
    mocker.patch("cars_api.views.external_api_call", new=mock_external_api_call_raise_request_exception)
    # create car with mocked response from external api
    car_make = "Honda"
    car_model = "Civic"
    expected_response = {"external_api_error": ""}
    response = client.post("/cars/", {"make": {car_make}, "model": {car_model}})
    # validate results
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == expected_response
    assert len(Car.objects.all()) == 0


@add_marks("positive_case", "get", "cars_endpoint")
@pytest.mark.django_db(reset_sequences=True)
def test_get_cars_endpoint_positive_case_multiple_car_records(db_with_multiple_car_records, client):
    # get list of cars
    expected_response = [
        {"id": 2, "make": "Civic", "model": "Honda", "avg_rating": None},
        {"id": 1, "make": "Accord", "model": "Honda", "avg_rating": None},
        {"id": 3, "make": "Pilot", "model": "Honda", "avg_rating": None},
    ]
    response = client.get("/cars/")
    # validate results
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_response
    assert len(Car.objects.all()) == 3


@add_marks("positive_case", "get", "cars_endpoint")
@pytest.mark.django_db(reset_sequences=True)
def test_get_cars_endpoint_positive_case_no_cars(client):
    # get list of cars
    expected_response = []
    response = client.get("/cars/")
    # validate results
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_response
    assert len(Car.objects.all()) == 0


@add_marks("positive_case", "del", "cars_endpoint")
@pytest.mark.django_db(reset_sequences=True)
def test_delete_cars_endpoint_positive_case(db_with_multiple_car_records, client):
    # get list of cars
    expected_response = [
        {"id": 2, "make": "Civic", "model": "Honda", "avg_rating": None},
        {"id": 1, "make": "Accord", "model": "Honda", "avg_rating": None},
        {"id": 3, "make": "Pilot", "model": "Honda", "avg_rating": None},
    ]
    response = client.get("/cars/")
    # validate results, 3 cars in db
    assert response.status_code == status.HTTP_200_OK
    assert len(Car.objects.all()) == 3
    assert response.data == expected_response
    assert Car.objects.get(pk=1) is not None

    # remove car with pk=1
    expected_response = {"message": "Record deleted"}
    response = client.delete("/cars/1/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_response
    assert len(Car.objects.all()) == 2
    # get list of cars, verify that there are only 2 in db
    expected_response = [
        {"id": 2, "make": "Civic", "model": "Honda", "avg_rating": None},
        {"id": 3, "make": "Pilot", "model": "Honda", "avg_rating": None},
    ]
    response = client.get("/cars/")
    assert response.data == expected_response


@add_marks("negative_case", "del", "cars_endpoint")
@pytest.mark.django_db(reset_sequences=True)
def test_delete_cars_endpoint_negative_case_record_does_not_exist(client):
    # verify that there is no car records
    assert len(Car.objects.all()) == 0
    # remove car with pk=1
    expected_response = {"validation_error": "Record doesn't exist"}
    response = client.delete("/cars/1/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data == expected_response


@add_marks("positive_case", "post", "rate_endpoint")
@pytest.mark.django_db(reset_sequences=True)
def test_post_rate_endpoint_positive_case(client, db_with_single_car_record):
    # add rating to car
    expected_response = {"car_id": 1, "rating": 5}
    response = client.post("/rate/", {"car_id": 1, "rating": 5})
    assert response.status_code == status.HTTP_201_CREATED
    assert len(Rate.objects.all()) == 1
    assert response.data == expected_response

    # get list of cars
    expected_response = [
        {"id": 1, "make": "Civic", "model": "Honda", "avg_rating": 5},
    ]
    response = client.get("/cars/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_response

    # add another rating to car
    expected_response = {"car_id": 1, "rating": 4}
    response = client.post("/rate/", {"car_id": 1, "rating": 4})
    assert response.status_code == status.HTTP_201_CREATED
    assert len(Rate.objects.all()) == 2
    assert response.data == expected_response
    # get list of cars
    expected_response = [
        {"id": 1, "make": "Civic", "model": "Honda", "avg_rating": 4.5},
    ]
    response = client.get("/cars/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_response


@add_marks("negative_case", "post", "rate_endpoint")
@pytest.mark.django_db(reset_sequences=True)
def test_post_rate_endpoint_negative_case_rating_out_of_range(client, db_with_single_car_record):
    # add rating to car
    expected_response = {"rating": [ErrorDetail(string="Rating has to be between 1 and 5.", code="max_value")]}
    response = client.post("/rate/", {"car_id": 1, "rating": 7})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(Rate.objects.all()) == 0
    assert response.data == expected_response

    expected_response = {"rating": [ErrorDetail(string="Rating has to be between 1 and 5.", code="min_value")]}
    response = client.post("/rate/", {"car_id": 1, "rating": -3})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(Rate.objects.all()) == 0
    assert response.data == expected_response


@add_marks("negative_case", "post", "rate_endpoint")
@pytest.mark.django_db(reset_sequences=True)
def test_post_rate_endpoint_negative_case_no_car_record(client):
    # add rating to car
    expected_response = {"car_id": [ErrorDetail(string="Car record does not exist.", code="does_not_exist")]}
    response = client.post("/rate/", {"car_id": 1, "rating": 4})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(Rate.objects.all()) == 0
    assert response.data == expected_response


@add_marks("negative_case", "post", "rate_endpoint")
@pytest.mark.django_db(reset_sequences=True)
def test_post_rate_endpoint_negative_case_no_rate_param(client, db_with_single_car_record):
    # add rating to car"rating": [
    expected_response = {"rating": [ErrorDetail(string="This field is required.", code="required")]}
    response = client.post("/rate/", {"car_id": 1})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(Rate.objects.all()) == 0
    assert response.data == expected_response


@add_marks("negative_case", "post", "rate_endpoint")
@pytest.mark.django_db(reset_sequences=True)
def test_post_rate_endpoint_negative_case_no_car_id_param(client):
    # add rating to car"rating": [
    expected_response = {"car_id": [ErrorDetail(string="This field is required.", code="required")]}
    response = client.post("/rate/", {"rating": 1})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(Rate.objects.all()) == 0
    assert response.data == expected_response


@add_marks("positive_case", "get", "popular_endpoint")
@pytest.mark.django_db(reset_sequences=True)
def test_get_popular_endpoint_positive_case(client, db_with_multiple_car_and_rating_records):
    # get list of cars
    expected_response = [
        OrderedDict([("id", 3), ("make", "Pilot"), ("model", "Honda"), ("rates_number", 3)]),
        OrderedDict([("id", 2), ("make", "Civic"), ("model", "Honda"), ("rates_number", 2)]),
        OrderedDict([("id", 1), ("make", "Accord"), ("model", "Honda"), ("rates_number", 1)]),
    ]
    response = client.get("/popular/")
    # validate results
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_response


"""######### Models Tests #########"""


@add_marks("aux", "model")
def test_car_model_aux_methods():
    car = Car(model="Honda", make="Accord")
    assert str(car) == "Honda Accord"
    assert car.to_dict() == {"make": "Accord", "model": "Honda"}


@add_marks("aux", "model")
def test_rate_mode_aux_methods():
    car = Car(model="Honda", make="Accord")
    rate = Rate(car_id=car, rating=4)
    assert str(rate) == f"{str(car)}: 4"
    assert rate.to_dict() == {"car": {"make": "Accord", "model": "Honda"}, "rate": 4}


"""######### Aux Tests #########"""


@add_marks("aux", "external_api", "negative_case")
def test_external_api_call_negative_case_raises_attribute_error():
    factory = APIRequestFactory()
    request = factory.get("")
    with pytest.raises(AttributeError, match="Wrong request method \\(post required\\) or missing api url env variable"):
        external_api_call(request, "", "")  # type: ignore


@add_marks("aux", "external_api", "negative_case")
def test_external_api_call_negative_case_raises_connection_error(mocker):
    factory = APIRequestFactory()
    request = factory.post("")
    mocker.patch(
        "cars_api.external_api.requests.get", return_value=MockResponse(json_data={}, status_code=status.HTTP_400_BAD_REQUEST)
    )

    with pytest.raises(ConnectionError, match="External api error or API unavailable"):
        external_api_call(request, "", "")  # type: ignore


@add_marks("aux", "external_api", "negative_case")
def test_external_api_call_negative_case_raises_value_error(mocker):
    mocked_response_data = {
        "Count": 1,
        "Message": "Response returned successfully",
        "SearchCriteria": "Make:honda",
        "Results": [
            {"Make_ID": 474, "Make_Name": "HONDA", "Model_ID": 1861, "Model_Name": "Accord"},
        ],
    }
    factory = APIRequestFactory()
    request = factory.post("")
    mocker.patch(
        "cars_api.external_api.requests.get",
        return_value=MockResponse(
            json_data=mocked_response_data,
            status_code=status.HTTP_200_OK,
        ),
    )

    with pytest.raises(ValueError, match="No matching result in external api for Honda Civic"):
        external_api_call(request, car_make="Honda", car_model="Civic")  # type: ignore


@add_marks("aux", "external_api", "positive_case")
def test_external_api_call_positive_case(mocker):
    mocked_response_data = {
        "Count": 1,
        "Message": "Response returned successfully",
        "SearchCriteria": "Make:honda",
        "Results": [
            {"Make_ID": 474, "Make_Name": "HONDA", "Model_ID": 1861, "Model_Name": "Accord"},
        ],
    }
    factory = APIRequestFactory()
    request = factory.post("")
    mocker.patch(
        "cars_api.external_api.requests.get",
        return_value=MockResponse(
            json_data=mocked_response_data,
            status_code=status.HTTP_200_OK,
        ),
    )

    resp = external_api_call(request, car_make="Honda", car_model="Accord")  # type: ignore

    assert resp == [{"Make_ID": 474, "Make_Name": "HONDA", "Model_ID": 1861, "Model_Name": "Accord"}]
