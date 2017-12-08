init:
	pip3 install -r requirements.txt -t lib

test:
	PYTHONPATH=./lib:. /usr/bin/env python3 -m lib.pytest --ignore=lib

dist: lib
	pyinstaller BeeVeeH.spec



.PHONY: dist