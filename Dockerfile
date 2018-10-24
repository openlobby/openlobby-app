FROM python:3.7-alpine

RUN mkdir /code
WORKDIR /code
COPY requirements.txt ./
RUN pip install -r requirements.txt && pip install gunicorn
COPY . ./

EXPOSE 8020

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8020", "--access-logfile", "-", \
     "--error-logfile", "-", "--capture-output", "olapp.wsgi"]
