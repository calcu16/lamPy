SUBMODULES =  $(wildcard modules/*)
HANDLERS = handler setup

TARGETS = .htaccess $(HANDLERS:%=%.py) $(SUBMODULES:%=%/README.md)

all: $(TARGETS)

clean:
	rm -rf $(TARGETS) __pycache__ scripts/__pycache__

.SECONDEXPANSION:

.htaccess: .htaccess.template
	cp .htaccess.start .htaccess && chmod 777 .htaccess

$(HANDLERS:%=%.py): scripts/$$@
	echo '#!'`which python3` | cat - $< > $@
	chmod 755 $@

$(SUBMODULES:%=%/README.md):
	git submodule init $(@D)
	git submodule update $(@D)
	cd $(@D) && git checkout master

