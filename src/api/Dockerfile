FROM python:3.12.0-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r /app/requirements.txt

COPY . /app

CMD ["flask", "--app", "main", "run", "--host", "0.0.0.0"]