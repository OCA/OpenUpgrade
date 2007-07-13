all: create package uninstall install

create:
	cat import script/lib/actions.py script/lib/error.py script/lib/functions.py script/lib/gui.py script/Repeatln.py script/Fields.py script/Expression.py script/modify.py script/ServerParameter.py > package/TinyERPReport.py

package:
	rm -f tinyreport.zip
	zip -r tinyreport.zip package/*
	
install:
	sh /usr/lib/openoffice/program/unopkg add -v tinyreport.zip
	
uninstall:
	sh /usr/lib/openoffice/program/unopkg remove -v  tinyreport.zip
