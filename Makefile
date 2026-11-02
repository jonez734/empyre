PROJECT = empyre
THUMB = /run/media/jam/BEA6-BBCE/
VENV_DIR ?= $(or $(DEPLOY_PREFIX),$(HOME)/.venv)
VENV_PYTHON ?= python3.12
# bbsengine6 is a sibling checkout; its own venv target installs the engine wheel into VENV_DIR.
BBSENGINE6_DIR ?= ../bbsengine6

all:

clean:
	-rm *~
	$(MAKE) -C src clean

push:
	git push

version:
	@echo '__version__ = "'`git log -1 --format='%H' | cut -c 1-16`'"' > empyre/_version.py
	@echo '__datestamp__ = "'`date +%Y%m%d-%H%M`-`whoami`'"' >> empyre/_version.py

# venv: a local .venv with empyre installed from a wheel built out of src/. The build runs in
# a scratch copy so the tree is not touched (no _version.py rewrite, no build/ or egg-info left).
venv:
	@if [ ! -x "$(VENV_DIR)/bin/python" ]; then \
		command -v "$(VENV_PYTHON)" >/dev/null 2>&1 || { echo "venv: $(VENV_PYTHON) not found; install it or set VENV_PYTHON" >&2; exit 1; }; \
		"$(VENV_PYTHON)" -m venv "$(VENV_DIR)" || { echo "venv: could not create $(VENV_DIR)" >&2; exit 1; }; \
	fi
	"$(VENV_DIR)/bin/python" -m pip install --upgrade pip
	"$(VENV_DIR)/bin/python" -m pip install --upgrade build
	@work="$$(mktemp -d)" && \
	trap 'rm -rf "$$work"' EXIT && \
	mkdir "$$work/src" && \
	tar -C src --exclude=./dist --exclude='*.egg-info' --exclude=__pycache__ -cf - . | tar -C "$$work/src" -xf - && \
	"$(VENV_DIR)/bin/python" -m build --wheel --outdir "$$work/out" "$$work/src" && \
	whl="$$(ls "$$work"/out/*.whl)" && \
	"$(VENV_DIR)/bin/python" -c "import bbsengine6" 2>/dev/null || \
		$(MAKE) -C "$(BBSENGINE6_DIR)" venv DEPLOY_PREFIX="$(abspath $(VENV_DIR))" VENV_PYTHON="$(VENV_PYTHON)" && \
	"$(VENV_DIR)/bin/python" -m pip install --upgrade "psycopg[binary,pool]" psycopg-pool python-dateutil requests argcomplete bcrypt markdown websockets && \
	"$(VENV_DIR)/bin/python" -m pip install --upgrade --force-reinstall --no-deps "$$whl" && \
	echo "empyre installed into $(VENV_DIR)"

build: version
	$(VENV_PYTHON) -m build --outdir dist src

sdist: version
	$(VENV_PYTHON) -m build --sdist --outdir dist src

install: build
	sudo $(VENV_PYTHON) -m pip install --force-reinstall --no-deps dist/*.whl

backup:
	rsync --recursive --verbose --exclude=.venv . $(THUMB)work/$(PROJECT)/

deploy: version
	python3 -m build --outdir dist
	$(MAKE) -C www prod
