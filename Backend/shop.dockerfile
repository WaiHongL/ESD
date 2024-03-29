FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./shop.py ./
CMD [ "python", "./shop.py" ]

# docker build -t g4t3/shop:1.0 -f shop.dockerfile .
# docker run -p 5000:5000 -e dbURL=mysql+mysqlconnector://root:pSSSS+]q8zZ-pjF:@host.docker.internal:3306/shop g4t3/shop:1.0