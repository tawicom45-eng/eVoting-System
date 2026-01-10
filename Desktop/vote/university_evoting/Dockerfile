FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# system deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install python deps
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# copy project
COPY . /app/

# create entrypoint and ensure permissions
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PATH="/root/.local/bin:$PATH"

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "evoting_system.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "2"]
