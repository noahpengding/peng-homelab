FROM python:3.11.11-slim-bullseye

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv>=0.6.6
RUN uv venv .venv
RUN uv pip install .

ENV TZ=America/Toronto

RUN apt-get update && apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

COPY . .

CMD ["uv", "run", "--active", "/app/main.py"]
