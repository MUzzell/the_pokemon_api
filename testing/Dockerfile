FROM python:latest

COPY . /testing
RUN pip install -r /testing/requirements.txt

WORKDIR /testing

CMD ["pytest", "-vv"]