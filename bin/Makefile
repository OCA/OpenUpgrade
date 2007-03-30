all:
	rm -f tinyreport.zip
	zip -r tinyreport.zip package/*

install:
	sh /usr/lib/openoffice/program/unopkg add -v tinyreport.zip

uninstall:
	sh /usr/lib/openoffice/program/unopkg remove -v  tinyreport.zip
