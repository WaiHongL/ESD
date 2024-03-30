FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./refund_game.py ./amqp_connection.py ./invokes.py ./
#
CMD [ "python", "./refund_game.py" ]