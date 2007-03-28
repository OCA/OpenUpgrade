all:
	rm -f tinyreport.zip
	zip -r tinyreport.zip package/*

install:
	/usr/lib/openoffice/program/unopkg add tinyreport.zip

uninstall:
	/usr/lib/openoffice/program/unopkg remove tinyreport.zip
