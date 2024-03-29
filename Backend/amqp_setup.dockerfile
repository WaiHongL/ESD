FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./amqp_setup.py ./amqp_connection.py ./
CMD [ "python", "./amqp_setup.py" ]
