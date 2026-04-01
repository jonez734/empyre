# Makefile for Smarty plugins
# Provides placeholder for custom Smarty plugin structure
# @since 20260401
# 
# Custom Smarty plugins can be placed in this directory
# They will be available to templates through config\SMARTYPLUGINSDIR configuration

stage:
	$(RSYNC) *.php $(STAGE)smarty/ 2>/dev/null || true

clean:
	-rm *~
