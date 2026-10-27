.PHONY: install run test verify container
install:
	python -m pip install -e '.[dev]'
run:
	uvicorn app.main:app --reload
test:
	pytest -q
verify:
	ruff check .
	pytest -q
container:
	docker build -t geoquanta .
