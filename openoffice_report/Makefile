all: create pack uninstall install

create:
	cat script/import \
	    script/lib/actions.py \
	    script/lib/error.py \
	    script/lib/functions.py \
	    script/lib/gui.py \
	    script/lib/tools.py \
	    script/LoginTest.py \
	    script/AddAttachment.py \
	    script/ServerParameter.py \
	    script/About.py > package/OpenERPReport.py

pack:
	rm -f openerp_report.zip
	zip -r openerp_report.zip package/*
	
install:
	sh /usr/lib/openoffice/program/unopkg add -v openerp_report.zip
	
uninstall:
	sh /usr/lib/openoffice/program/unopkg remove -v  openerp_report.zip
