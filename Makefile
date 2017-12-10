init:
	pip3 install -r requirements.txt -t lib

init-accelerated:
	/usr/bin/env sh init-accelerated.sh

run:
	PYTHONPATH=./lib:. /usr/bin/env python3 -m main

test:
	PYTHONPATH=./lib:. /usr/bin/env python3 -m lib.pytest --ignore=lib

testv:
	PYTHONPATH=./lib:. /usr/bin/env python3 -m tests.test_app

dist:
	rm -rf dist 2>/dev/null
	PYTHONPATH=./lib:. /usr/bin/env python3 -m lib.PyInstaller BeeVeeH.spec



.PHONY: dist