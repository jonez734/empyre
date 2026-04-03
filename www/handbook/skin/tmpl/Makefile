all:

stage:
	rsync --delete-after --chmod=Dg=rwxs,Fgu=rw,Fo=r --verbose --archive --update --backup --recursive --human-readable --rsh=ssh --no-owner --no-group --checksum --mkpath *.tmpl /srv/www/vhosts/zoidtechnologies.com/html/empyre/handbook/tmpl/

clean:
	-rm *~

.PHONY: clean stage
