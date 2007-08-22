all: create pack uninstall install

create:
	cat import script/lib/actions.py script/lib/error.py script/lib/functions.py script/lib/gui.py script/Repeatln.py script/Fields.py script/Expression.py script/modify.py script/ServerParameter.py script/Change.py script/NewReport.py script/LoginTest.py script/ModifyExistingReport.py script/SendToServer.py script/About.py script/ConvertBracesToField.py script/ConvertFieldsToBraces.py > package/TinyERPReport.py

pack:
	rm -f tinyreport.zip
	zip -r tinyreport.zip package/*
	
install:
	sh /usr/lib/openoffice/program/unopkg add -v tinyreport.zip
	
uninstall:
	sh /usr/lib/openoffice/program/unopkg remove -v  tinyreport.zip
