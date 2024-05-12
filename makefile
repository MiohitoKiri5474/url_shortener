version = $(shall cat package | grep version | awk -F '"' '{print $$4}')

install:
	pip3 install poetry black isort
	poetry install

run:
	poetry run uvicorn app.main:app

lint:
	isort app/*.py tests/*.py
	black app/*.py tests/*.py

test:
	poetry run pytest
