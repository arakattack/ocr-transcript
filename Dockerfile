FROM python:3.12.4-slim-bullseye
ENV GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
    PROJECT_ID=$PROJECT_ID \
    LOCATION_ID=$LOCATION_ID \
    PROCESSOR_ID=$PROCESSOR_ID \
    MODEL_VERSION=$MODEL_VERSION \
    API_KEY=$API_KEY

WORKDIR /usr/src/app
COPY . .
RUN apt-get update
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# CMD [ "gunicorn", "api:app --workers 4 --threads 2 --worker-class gevent --keep-alive 5 --timeout 30 --worker-connections 1000" ]


EXPOSE 80