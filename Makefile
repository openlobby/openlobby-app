init-env:
	python3 -m venv .env

install:
	pip install -r requirements.txt

test:
	pytest

run:
	python manage.py runserver 8020

build:
	docker build -t openlobby/openlobby-app:latest .

push:
	docker push openlobby/openlobby-app:latest
