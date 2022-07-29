PY = python3
VENV = venv
BIN = $(VENV)/bin

TEST_DIR = tests

ifeq ($(OS), Windows_NT)
	BIN = $(VENV)/Scripts
	PY = python
endif

$(VENV): 
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --upgrade -r requirements.txt
	$(BIN)/pip install -e .
	touch $(VENV)

.PHONY: test clean init $(VENV)

init: $(VENV)
	mkdir -p tests/build

test: $(VENV) init
	$(BIN)/python3 -m unittest discover

clean: 
#	rm -rf $(VENV)
	rm -rf tests/build
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete