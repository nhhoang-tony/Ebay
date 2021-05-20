
FROM python:3.6-alpine

COPY . /opt/

EXPOSE 8080

WORKDIR /opt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ="Australia/Sydney"

RUN pip install -r requirements.txt && \
    echo $TZ > /etc/timezone && \
    ln -sf /usr/share/zoneinfo/$TZ /etc/localtime
    

ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8080"]