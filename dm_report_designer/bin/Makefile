ZIP_FILE=dm_report_designer.zip

all: pack uninstall install

create:
	cat script/import \
	    script/lib/actions.py \
	    script/lib/error.py \
	    script/lib/functions.py \
	    script/lib/gui.py \
	    script/lib/tools.py \
	    script/ServerParameter.py \
	    script/LoginTest.py \
	    script/ModifyExistingReport.py \
	    script/SendToServer.py \
	    script/About.py \
	    script/DirectMarketing.py \
	    script/AddFields.py \
		script/DmLoop.py \
	    script/AddImage.py > package/OpenERPReport.py

pack: clean create
	zip $(ZIP_FILE) `find package/ | grep -v svn` 
	
install:
	sh /usr/lib/openoffice/program/unopkg add -v $(ZIP_FILE)
	
uninstall:
	sh /usr/lib/openoffice/program/unopkg remove -v  $(ZIP_FILE)

clean:
	rm -f $(ZIP_FILE)