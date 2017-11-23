FROM python:3.6-slim

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install gunicorn
ADD . /code/

EXPOSE 8020

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8020", "--access-logfile", "-", \
     "--error-logfile", "-", "--capture-output", "olapp.wsgi"]
