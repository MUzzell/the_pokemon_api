FROM python:latest

COPY . /backend
RUN pip install -r /backend/requirements.txt

WORKDIR /backend

RUN cd /backend && python setup.py develop

CMD ["python", "-m", "backend"]