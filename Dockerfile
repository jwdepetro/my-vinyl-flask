FROM python:3-alpine

WORKDIR /opt/services/flaskapp/src

COPY requirements.txt .

RUN apk update && \
    apk add postgresql-libs && \
    apk add --no-cache bash && \
    apk add --virtual .build-deps gcc musl-dev postgresql-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

COPY . .

EXPOSE 5090

CMD ["/bin/bash", "entrypoint.sh"]