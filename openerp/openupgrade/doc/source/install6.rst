Step 2: Setup OpenERP 6 database
================================

Next, we repeat the process for version 6.

Install the openupgrade server version 6. Configure logging to file.
Create a new database. Install the module that you want to write an upgrade
script for.
Stop the openupgrade server version 6
Delete the server log file.
Start the openupgrade server with -u all -d <database> --stop-after-init

Extract a csv file with the database layout per module, using the following
command::

	grep OpenUpgrade_FIELD <server-6.log> |cut -d \: -f 5- | sort > server-6.csv

Extract a text file with the XML IDs created per module, using the following
command::

	grep OpenUpgrade_XMLID <server-6.log> |cut -d \: -f 5- | sort > xmlids-6.txt

Perform a rough matching mechanism on the csv files:

	/path/to/openupgrade-server/bin/openupgrade/process-csv.py server-5.csv server-6.csv

Save the results as a starting point for your work. See below for a description
of the output.
