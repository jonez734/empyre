all:

clean:
	-rm *~
	$(MAKE) -C empyre clean
	$(MAKE) -C bin clean

push:
	git push

version:
	@echo '__version__ = "'`git log -1 --format='%H' | cut -c 1-16`'"' > empyre/_version.py
	@echo '__datestamp__ = "'`date +%Y%m%d-%H%M`-`whoami`'"' >> empyre/_version.py

install: version build
	sudo ./setup.py install

build: version
	./setup.py build

sdist: version
	./setup.py sdist
