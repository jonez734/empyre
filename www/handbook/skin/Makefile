all: scss tmpl

scss:
	$(MAKE) -C scss

tmpl:
	$(MAKE) -C tmpl

clean:
	$(MAKE) -C scss clean
	$(MAKE) -C tmpl clean

stage:
	$(MAKE) -C scss stage
	$(MAKE) -C tmpl stage

.PHONY: all scss tmpl clean stage
