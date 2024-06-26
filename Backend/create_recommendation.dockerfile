FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./create_recommendation.py ./amqp_connection.py ./invokes.py ./
CMD [ "python", "./create_recommendation.py" ]