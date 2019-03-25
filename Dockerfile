from python:3.7-alpine3.9

RUN apk add --no-cache gcc libc-dev libxml2-dev libffi-dev
RUN apk add --no-cache libxslt-dev python-dev
RUN apk add --no-cache openssl-dev
RUN pip install --upgrade pip
RUN pip install pipenv

WORKDIR /app
COPY . /app/
RUN rm -rf .venv
RUN rm -rf .env
RUN rm -rf Pipfile.lock
RUN pipenv lock -r > requirements.txt
RUN pip install -r requirements.txt

CMD python test.py
