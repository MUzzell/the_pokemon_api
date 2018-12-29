FROM python:latest

COPY . /backend
RUN pip install -r /backend/requirements.txt

WORKDIR /backend

CMD ["python", "app.py"]