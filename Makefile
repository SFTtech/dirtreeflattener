default:
	@echo "make install or make uninstall"

install:
	install dtf -t /usr/bin
	install -d /usr/lib/python3.3/site-packages/dirtreeflattener
	install dirtreeflattener/*.py -t /usr/lib/python3.3/site-packages/dirtreeflattener

uninstall:
	rm /usr/bin/dtf
	rm -r /usr/lib/python3.3/site-packages/dirtreeflattener

.PHONY: default install uninstall
