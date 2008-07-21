all: create pack uninstall install

create:
	cat import \
	    script/lib/actions.py \
	    script/lib/error.py \
	    script/lib/functions.py \
	    script/lib/gui.py \
	    script/lib/tools.py \
	    script/Repeatln.py \
	    script/Fields.py \
	    script/Expression.py \
	    script/modify.py \
	    script/ServerParameter.py \
	    script/Change.py \
	    script/NewReport.py \
	    script/LoginTest.py \
	    script/ModifyExistingReport.py \
	    script/SendToServer.py \
	    script/About.py \
	    script/ConvertBracesToField.py \
	    script/ConvertFieldsToBraces.py \
	    script/ExportToRML.py \
	    script/Translation.py \
	    script/AddAttachment.py > package/OpenERPReport.py

pack:
	rm -f openerp_report_designer.zip
	zip openerp_report_designer.zip `find package/ | grep -v svn` 
	
install:
	sh /usr/lib/openoffice/program/unopkg add -v openerp_report_designer.zip
	
uninstall:
	sh /usr/lib/openoffice/program/unopkg remove -v  openerp_report_designer.zip
