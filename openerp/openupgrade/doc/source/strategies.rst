Analysis and development strategies
+++++++++++++++++++++++++++++++++++

Second stage database comparison
================================
After an initial migration, performing the database comparison again but now comparing the results of your migration with a database created on your target release will give you more information on any data (marked as *noupdate*) that you might have missed.

Testing on a database with demo data
====================================
Testing your upgrade script on a database with demo data is a useful
excercise. However, this will trigger a run of the yaml test suite. A number
of tests are bound to fail due to addition leftover data (such as currency
rates). This is harmless and not a problem with your migration scripts.

Skipping releases
=================
You *can* create an upgrade script that skips one or
more major releases of OpenERP, but such a script will be useless for other
users and developers of the OpenUpgrade distribution. If you can, please create
all the intermediate scripts.
