.PHONY: install build test run docker-build docker-run clean

install:
	pip install -r requirements.txt

build:
	python -m compileall medbill

test:
	python tests/runner.py

run:
	python main.py

docker-build:
	docker build -t medbill-enterprise:latest .

docker-run:
	docker run -p 8080:8080 medbill-enterprise:latest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
