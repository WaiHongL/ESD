FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./make_purchase.py ./amqp_connection.py ./invokes.py ./
#RUN python amqp_setup.py
CMD [ "python", "./make_purchase.py" ]