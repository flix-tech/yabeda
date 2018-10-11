
.PHONY: run-locally


install:
	python3 -m pip install -r requirements.txt

run-locally:
	export PYTHONPATH=$(pwd)
	python3 -m yabeda

test:
	pytest
