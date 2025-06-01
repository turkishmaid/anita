SHELL := $(SHELL)

it: local/fridge.txt

local:
	mkdir local
	
venv:
	python3.13 -m venv venv
	. venv/bin/activate; pip install --upgrade pip

local/fridge.txt: requirements.txt venv local
	. venv/bin/activate; pip install -r requirements.txt
	. venv/bin/activate; pip freeze > local/fridge.txt
