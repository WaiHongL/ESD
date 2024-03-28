FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./user.py .
CMD [ "python", "./user.py" ]

# Run in terminal to test: 
# docker build -t g4t3/user:1.0 -f user.dockerfile .
# docker run -p 5101:5000 -e dbURL=mysql+mysqlconnector://root:pSSSS+]q8zZ-pjF:@host.docker.internal:3306/user g4t3/user:1.0