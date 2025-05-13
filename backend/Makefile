POETRY = ${POETRY_HOME}/bin/poetry
sources = app tests

.PHONY: run
run:
	$(POETRY) run python3 -m app

.PHONY: install
install:
	$(POETRY) install

.PHONY: format
format:
	$(POETRY) run ruff check --fix $(sources)
	$(POETRY) run ruff format $(sources)

.PHONY: lint
lint:
	$(POETRY) run ruff check $(sources)
	$(POETRY) run mypy

.PHONY: test
test:
	$(POETRY) run coverage run -m pytest -vvv
	$(POETRY) run coverage report

.PHONY: clean
clean:
	rm -rf .mypy_cache .coverage .ruff_cache .pytest_cache

.PHONY: fclean
fclean: clean
	rm -rf .venv
