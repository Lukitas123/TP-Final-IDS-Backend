FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y python3.10 python3-pip
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"]
