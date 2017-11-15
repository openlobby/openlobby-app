init-env:
	python3 -m venv .env

install:
	pip install -r requirements.txt

run:
	DEBUG=1 python manage.py runserver 8020

build:
	docker build -t openlobby/openlobby-app:latest .

push:
	docker push openlobby/openlobby-app:latest

release:
	make build
	make push
