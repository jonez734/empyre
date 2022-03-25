all:

clean:
	-rm *~
push:
	git push origin master

version:
	@echo '__version__ = "'`git log -1 --format='%H' | cut -c 1-16`'"' > _version.py
