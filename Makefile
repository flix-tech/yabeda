
.PHONY: run-locally


install:
	python3 -m pip install -r requirements.txt

run-locally:
	uwsgi uwsgi.ini

test:
	pytest
