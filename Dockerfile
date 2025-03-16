FROM python:3

WORKDIR /ATRA

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y vim

CMD ["python","main.py"]