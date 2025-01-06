FROM python:3.10.12-slim-bookworm

WORKDIR /

COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app
COPY main.py /

ENV TZ=America/Toronto

RUN apt-get update && apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

CMD ["python", "/main.py"]