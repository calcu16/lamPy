
all: handler.py pypp .htaccess setup.py

clean:
	rm -rf .htaccess handler.py setup.py  __pycache__ scripts/__pycache__

.htaccess: .htaccess.template
	cp .htaccess.template .htaccess && chmod 755 .htaccess

handler.py: scripts/handler.py
	echo '#!'`which python3` | cat - scripts/handler.py > handler.py && chmod 755 handler.py

setup.py: scripts/setup.py
	echo '#!'`which python3` | cat - scripts/setup.py > setup.py && chmod 755 setup.py

pypp: scripts/pypp/__init__.py

scripts/pypp/__init__.py:
	git submodule init pypp
	git submodule update pypp

