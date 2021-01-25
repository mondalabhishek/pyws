FROM python:3.9.1

WORKDIR /app

COPY ./app.py /app
COPY ./requirement.txt /app

RUN pip3 install -r requirement.txt

EXPOSE 5001

CMD python3 app.py