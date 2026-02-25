PROJECT = empyre
OUTDIR = /srv/repo/$(PROJECT)/
VERSION = $(shell date +%Y%m%d%H%M)

PYTHON = python3

.PHONY: build version
.PHONY: clean build rename-sdist sign release all

all:

clean:
	-rm *~
	$(MAKE) -C empyre clean
	$(MAKE) -C bin clean

push:
	git push

version:
	@echo 'githash = "'`git log -1 --format='%H' | cut -c 1-16`'"' > $(PROJECT)/_version.py
	@echo 'datestamp = "$(VERSION)"' >> $(PROJECT)/_version.py

build:
	VERSION=$(VERSION) $(PYTHON) -m build --outdir $(OUTDIR)

rename-sdist:
	@for f in $(OUTDIR)/*.tar.gz; do \
        	if [ -f "$$f" ] && echo "$$f" | grep -vq '\-src\.tar\.gz' ; then \
                	mv "$$f" "$${f%.tar.gz}-src.tar.gz"; \
			echo "Renamed $$f -> $${f%.tar.gz}-src.tar.gz"; \
		fi \
	done

sign:
	@for f in $(OUTDIR)/*; do \
        	if [ -f "$$f" ] && [ ! -f "$$f.asc" ] && [ "$${f##*.}" != "asc" ]; then \
                	gpg --armor --detach-sign "$$f"; \
			echo "Signed $$f"; \
		fi \
	done

release: clean version build rename-sdist sign

sdist:
	$(PYTHON) -m setup sdist --dist-dir /srv/repo/$(PROJECT)/
