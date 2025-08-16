FROM python:3.13-slim

WORKDIR /ATRA

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python","main.py"]