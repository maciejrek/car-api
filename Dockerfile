# pull official base image
FROM python:3

WORKDIR /code

# install dependencies
COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

# run entrypoint.sh
ENTRYPOINT [ "/code/entrypoint.sh" ]

# run gunicorn
CMD gunicorn app.wsgi:application --bind 0.0.0.0:$PORT --timeout 30