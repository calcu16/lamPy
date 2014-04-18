
NODE_V = node-v0.10.5-linux-x64

SUBMODULES = bootstrap $(wildcard modules/*)
HANDLERS = handler setup
SUBSYSTEMS = # bootstrap

TARGETS = .htaccess $(HANDLERS:%=%.py) $(SUBMODULES:%=%/README.md) $(SUBSYSTEMS)

all: $(TARGETS)

clean:
	rm -rf $(TARGETS) __pycache__ scripts/__pycache__

.SECONDEXPANSION:
.INTERMEDIATE: $(NODE_V) $(NODE_V).tar.gz
.PHONY: $(SUBSYSTEMS)

.htaccess: .htaccess.template
	cp .htaccess.start .htaccess && chmod 755 .htaccess

$(HANDLERS:%=%.py): scripts/$$@
	echo '#!'`which python3` | cat - $< > $@
	chmod 755 $@

$(SUBMODULES:%=%/README.md):
	git submodule init $(@D)
	git submodule update $(@D)
	cd $(@D) && git checkout master

node: $(NODE_V)
	mv $(NODE_V) node

$(NODE_V): $(NODE_V).tar.gz
	tar xfvz $@.tar.gz

$(NODE_V).tar.gz:
	wget http://nodejs.org/dist/v0.10.5/$@

bootstrap: node bootstrap/README.md bootstrap/.node_modules

bootstrap/.node_modules: node
	cd $(@D) && ../node/bin/npm install

# subsystems
$(SUBSYSTEMS): 
	cd $@ && $(MAKE)


	
