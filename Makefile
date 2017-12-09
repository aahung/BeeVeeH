init:
	pip3 install -r requirements.txt -t lib

test:
	PYTHONPATH=./lib:. /usr/bin/env python3 -m lib.pytest --ignore=lib

testv:
	PYTHONPATH=./lib:. /usr/bin/env python3 -m tests.test_app

dist: lib
	/usr/bin/env python3 -m lib.PyInstaller BeeVeeH.spec



.PHONY: dist