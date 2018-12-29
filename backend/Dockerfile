FROM python:latest

COPY . /backend
RUN pip install -r /backend/requirements.txt
RUN python /backend/setup.py develop

WORKDIR /backend

CMD ["python", "-m", "backend"]