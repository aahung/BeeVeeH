lib:
	pip3 install -r requirements.txt -t lib

run:
	./BeeVeeH.py

dist: lib
	pyinstaller BeeVeeH.spec

.PHONY: dist