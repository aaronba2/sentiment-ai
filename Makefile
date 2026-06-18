IMAGE_NAME=sentiment-ai
PORT=8080

.PHONY: build run test stop clean tag

build:
	docker build -t $(IMAGE_NAME):latest .

run:
	docker compose up -d

test:
	docker run --rm $(IMAGE_NAME):latest pytest tests -v

stop:
	docker compose down

clean:
	docker compose down
	docker rmi $(IMAGE_NAME):latest

tag:
	git tag -a v0.1.0 -m "Initial SentimentAI release"
	git push origin v0.1.0