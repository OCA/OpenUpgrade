.. OpenUpgrade documentation master file, created by sphinx-quickstart on Wed Nov 30 10:38:00 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to OpenUpgrade's documentation!
+++++++++++++++++++++++++++++++++++++++

Contents:

.. toctree::
   :maxdepth: 2

Database analysis
+++++++++++++++++

Below is an example of how you can review the differences between databases that
different versions of OpenERP generate, using a module based perspective.

The example is based on an upgrade between OpenERP 5 and 6.0, but it works the
same for 6.0 and 6.1.

As a sidenote, of course you *can* create an upgrade script that skips one or
more major releases of OpenERP, but such a script will be useless for other
users and developers of the OpenUpgrade distribution. If you can, please create
all the intermediate scripts.

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

XML ID's
========
Create a diff file of the XML ID's between the two database versions:

       diff xmlids-5.txt xmlids-6.txt > xmlids.diff

This will give you a clear overview of the resources that are created by the
modules. If you accidentally created the analysis from databases containing
demo data, you will get a lot of noise here. 

XML ID's which do not occur in the updated version of all installed modules
will be removed automatically by the OpenERP server. 

You can ignore most entries here, most notably

    ir.actions.*
    ir.model.fields
    ir.model
    ir.ui.* [1]
    res.country*
    res.currency*

More interesting are

    * res.groups
      If a res groups has moved module (example: hr_manager moved from module
      hr to base in OpenERP 6), implement this change in the pre-upgrade script
      for the module from which it moved.

    * res.roles (migrating from OpenERP 5 to 6 only)
      These have been migrated to groups in OpenERP6. Find out which group has
      replaced this role and use the role migration function from openupgrade
      library module (TODO).

    * workflow.*
      These ID's indicate changes in the workflow schemes. You need to map any
      of such changes in nodes and transitions, and replace them in the
      wkf\_ tables.

    * Option lists, such as ...?
      You may need to map the fields on any resources refering to this option
      list value to one of the new value set for this option.

    * ir.model.access
      In general, if you apply group access in line with the original meaning,
      you should be able to ignore these. However, you will need to audit the
      model access for your setup anyway. These entries might be of a little
      help in that process.

    * Any general data added by the module. Typically, data is loaded one time
      only using the 'noupdate' flag in the XML. You cannot simply force-load
      such data in your upgrade script, or you will for instance reset the
      sequences used for invoice numbering. Revise any data carefully and
      copy relevant, new data in a separate file. Load it from your post script
      using :meth:`~openupgrade.load_xml` from the module :mod:`openupgrade`
      which is included with the OpenUpgrade Server package. You may also have
      to update specific attributes from existing resources.

[1] You might want to use this information to semi automatically audit your
customizations. This subject falls out of scope of this project for now)

Fields analysis format
======================

The first section displays models which are removed from the database.
The second section displays models which are added to the database.

TODO: display which models moved to another module, instead of in the field
analysis? It should also be clear how to install such modules from the upgrade

The second section lists the model fields which have been signalled by the
analysis script. Every line lists the following columns:

module / model / field (field type) : description of the change

Multiple changes per field are listed on separate lines.
If possible, the old situation is added to the change description (in between
parentheses).

The change description flags the following types of change:

    * The field is now required. The upgrade script might apply the default for
      this field, if it is encoded in the model (see the openupgrade library
      function TODO). If any empty values remain, these can be reported by the
      openupgrade report module (TODO). 
      If the field is a function field after the upgrade, this changes the cause
      for action. See below.

    * A field is now a function or a related field. This might or might not call
      for any action of your upgrade script, as the value is now automatically
      determined. At the same time, this might cause data loss. An example is
      the field employee's manager (hr module), which in OpenERP 6 is derived
      from the employee's department.

      Without any action in the upgrade script, you will lose the manually
      encoded employee hierarchy.

    * A selection field's hardcoded selection changes. You need to audit the
      function for any change in possible values and may need to map any
      differences you encounter.

    * A selection field's selection is now being filled by a function or has
      stopped doing so. You need to audit the function for any change in
      possible values and may need to map any differences you encounter.

      (Of course, a selection function could change the set of posible values
      in between functions.)

    * The field changes type. This always calls for action in your upgrade
      script. Rename the database column to a temporary name in the pre script,
      then migrate the values in the post script. A typical instance of this
      change is when the field becomes a many2one lookup table, or the other way
      around. An example of these are the partner's function which became a char
      field in OpenERP 6, and the partner's title which as a selection (thus
      char type database column) and had to be migrated to a many2one on
      res.partner.title.

    * A relation field's relation changes. You need to migrate the one target
      model to the other, and update the references to them

    * A field is deleted from the model (marked by 'DEL'). Also fields from
      deleted models are marked in this way. TODO: mark fields from deleted
      models in a distinct manner. Any distinct features of the field are
      displayed, for easier manual matching.
      You need to audit any new fields
      (see below) to see if they correspond to the deleted field and implement
      this change in your upgrade script. It might also be the case that a
      deleted field is now delegated to a new or existing _inherits table (see below).

    * A field is introduced in the model (marked by 'NEW'). Also fields from
      introduced models are marked in this way. TODO: mark fields from introduced
      models in a distinct manner? Any distinct features of the field are
      displayed, for easier manual matching. You need to audit any deleted
      fields (see below) to see if they correspond to the new field and
      implement this change in your upgrade script.

    * The _inherits property of a model has changed. It might be the case that
      fields which are removed are actually delegated to this newly
      inherited table.

The final section of the database layout analysis contains a simple report on
the changes that were detected.

Note on testing on a database with demo data
============================================
Testing your upgrade script on a database with demo data is a useful
excercise. However, this will trigger a run of the yaml test suite. A number
of tests are bound to fail due to addition leftover data (such as currency
rates). This is harmless and not a problem with your migration scripts.

OpenUpgrade API
+++++++++++++++

You can use the following functions in your pre and post scripts.

.. automodule:: openupgrade.openupgrade
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

