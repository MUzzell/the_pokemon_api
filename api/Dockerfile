FROM python:latest

COPY . /api
RUN pip install -r /api/requirements.txt

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]