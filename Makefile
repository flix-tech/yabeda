
.PHONY: run-locally


install:
	python3 -m pip install -r requirements.txt

run-locally:
	uwsgi uwsgi.ini

test:
	python3 -m pytest \
	--cov=yabeda \
	--cov-branch \
	--cov-report=term-missing
