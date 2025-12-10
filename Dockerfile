FROM python:3.13-slim

RUN mkdir /chrisbot

WORKDIR /chrisbot

COPY ./jsonstuff.py .

COPY ./botcmds.py .

COPY ./requirements.txt .

COPY ./.env /chrisbot

RUN pip install -r requirements.txt

CMD ["python", "botcmds.py"]