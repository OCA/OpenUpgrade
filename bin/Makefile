create:
	cat import script/lib/*.py script/Repeatln.py script/Fields.py script/Expression.py script/modify.py pkgcode > package/TinyERPReport.py
	
all:
	rm -f tinyreport.zip
	zip -r tinyreport.zip package/*
	
install:
	sh /usr/lib/openoffice/program/unopkg add -v tinyreport.zip
	
uninstall:
	sh /usr/lib/openoffice/program/unopkg remove -v  tinyreport.zip