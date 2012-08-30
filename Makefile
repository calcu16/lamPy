
all: handler.py

clean:
	rm handler.py __pycache__

handler.py: scripts/handler.py
	echo '#!'`which python3` | cat - scripts/handler.py > handler.py && chmod 755 handler.py
