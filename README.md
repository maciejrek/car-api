# Car api readme

## How to start

Start API:

``` bash
docker-compose up --build
```
Migrations are being handled by docker-compose (./entrypoint.sh)

**MAKE SURE** [`docker`](https://docs.docker.com/get-docker/) and  [`docker-compose`](https://docs.docker.com/compose/install/) are installed.

## Env files
To run properly, there must be a few .env files (separated for each need)

1. app.env - env file for django app
```
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
DJANGO_DEBUG=1 <or remove this line to run without debu mode>
FROM_DOCKER=True
DJANGO_SECRET_KEY=<your_secret_key>
DJANGO_ALLOWED_HOSTS=localhost 0.0.0.0 127.0.0.1 [::1]

POSTGRES_ENGINE=django.db.backends.postgresql
POSTGRES_DB=<your_db_name>
POSTGRES_USER=<your_db_user>
POSTGRES_PASSWORD=<your_db_password>
POSTGRES_HOST=db
POSTGRES_PORT=5432

EXTERNAL_API_URL = https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake
```
2. db.env - used by postgres container
```
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```
3. local.env - used by tests, or to run app outside docker container
```
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
DJANGO_DEBUG=1
DJANGO_SECRET_KEY=<your_secret_key>
DJANGO_ALLOWED_HOSTS=localhost 0.0.0.0 127.0.0.1 [::1]

POSTGRES_ENGINE=django.db.backends.postgresql
POSTGRES_DB=<your_db_name>
POSTGRES_USER=<your_db_user>
POSTGRES_PASSWORD=<your_db_password>
POSTGRES_HOST=localhost
POSTGRES_PORT=8056

EXTERNAL_API_URL = https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake
```

To use one .env file make proper changes in app/settings.py and app/settings_pytest.py

To change any of the env_var names make proper changes in settings file and docker-compose.yml file

## Tests

Tests use [Pytest framework](https://docs.pytest.org/en/stable/) and pytest plugins: [Pytest cov](https://pytest-cov.readthedocs.io/en/latest/), [Pytest django](https://pytest-django.readthedocs.io/en/latest/), [Pytest mock](https://github.com/pytest-dev/pytest-mock/)
Tests are grouped, using pytest.markers. All markers can be found in setup.cfg file.

**KEEP IN MIND** that u need to have postgres database running, to run tests properly (just run the app with docker-compose up command, and then start tests localy or inside the container: docker-compose exec web pytest). 

To check coverage with information about missing lines, run

``` bash
pytest --cov-report term-missing --cov
```

It should produce the following result (values may differ):

``` bash
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
cars_api/external_api.py      18      0   100%
cars_api/models.py            22      0   100%
cars_api/views.py             51      0   100%
--------------------------------------------------------
TOTAL                        91      0   100%
```

To run only part of tests use

``` bash
pytest -m <marker>
```

It should produce the following result (values may differ):

``` bash
❯ pytest -m aux
collected 24 items / 18 deselected / 6 selected                                                                                                

cars_api/tests.py ...... [100%]

```

To see name of tests with result use -v

``` bash
❯ pytest -m aux -v
collected 24 items / 18 deselected / 6 selected                                                                                                

cars_api/tests.py::test_car_model_aux_methods PASSED                                     [ 16%]
cars_api/tests.py::test_rate_mode_aux_methods PASSED                                     [ 33%]
cars_api/tests.py::test_external_api_call_negative_case_raises_attribute_error PASSED    [ 50%]
cars_api/tests.py::test_external_api_call_negative_case_raises_connection_error PASSED   [ 66%]
cars_api/tests.py::test_external_api_call_negative_case_raises_value_error PASSED        [ 83%]
cars_api/tests.py::test_external_api_call_positive_case PASSED                           [100%]
```

## Postman Tests
There is car_api.postman_collection.json file stored in repository.
It contains postman collection, used during api tests. To use it simply import collection to the postman, and define **url** variable.

## Available endpoints:
[Api](https://vpic.nhtsa.dot.gov/api/)

/cars/

/cars/int:pk/

/popular/

/rate/


## Request Examples for each endpoint:

**Add new car if exists in external db:**
>[POST] /cars/
```bash
curl --location --request POST 'vast-meadow-68757.herokuapp.com/cars/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "make": "Volkswagen",
    "model": "Golf"
}'
```

**Fetch list of cars in application with avg rating (ordered by avg rating):**
>[GET] /cars/
```bash
curl --location --request GET 'vast-meadow-68757.herokuapp.com/cars/' \
--header 'Content-Type: application/json''
```

**Delete car with given pk:**
>[DEL] /cars/{pk}/
```bash
curl --location --request DELETE 'vast-meadow-68757.herokuapp.com/cars/1/' \
--header 'Content-Type: application/json'
```

**Fetch list of cars in application with number of rate (ordered by num of rates - popularity):**
>[GET] /popular/
```bash
curl --location --request GET 'vast-meadow-68757.herokuapp.com/popular/' \
--header 'Content-Type: application/json'
```

**Add a rate for a car from 1 to 5:**
>[POST] /rate/
```bash
curl --location --request POST 'vast-meadow-68757.herokuapp.com/rate/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "car_id": 3,
    "rating": 2
}'
```
