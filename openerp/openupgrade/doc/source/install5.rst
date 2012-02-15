Step 1: Setup OpenERP 5 database
================================

Install the openupgrade server version 5. Configure logging to file.
Create a new database. Install the module that you want to write an upgrade
script for.
Stop the openupgrade server version 5
Delete the server log file.
Start the openupgrade server with -u all -d <database> --stop-after-init

Extract a csv file with the database layout per module, using the following
command::

	grep OpenUpgrade_FIELD <server-5.log> |cut -d \: -f 5- | sort > server-5.csv

Extract a text file with the XML IDs created per module, using the following
command::

	grep OpenUpgrade_XMLID <server-5.log> |cut -d \: -f 5- | sort > xmlids-5.txt

