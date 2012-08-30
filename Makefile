
all: handler.py

clean:
	rm handler.py

handler.py: scripts/handler.py
	echo '#!'`which python3` | cat - scripts/handler.py > handler.py
