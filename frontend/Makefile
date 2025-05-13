POETRY = ${POETRY_HOME}/bin/poetry
sources = app

.PHONY: run
run:
	$(POETRY) run streamlit run app.py

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

.PHONY: clean
clean:
	rm -rf .ruff_cache

.PHONY: fclean
fclean: clean
	rm -rf .venv
