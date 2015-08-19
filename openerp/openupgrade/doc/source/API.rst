OpenUpgrade API
+++++++++++++++

The OpenUpgrade library contains all kinds of helper functions for your pre and
post scripts, in OpenUpgrade itself or in the migration scripts of your own
module (in either major or minor version upgrades). It can be installed with

.. code-block:: bash

   pip install openupgradelib

and then used in your scripts as

.. code-block:: python

   from openupgradelib import openupgrade

General methods
---------------

.. automodule:: openupgrade
   :members:

Methods for OpenUpgrade 7.0
---------------------------

The following specific methods for 7.0 are available. These have been
developed to cover specific needs as per data model changes in that
release.

.. automodule:: openupgrade_70
   :members:

Methods for OpenUpgrade 8.0
---------------------------

The following specific methods for 8.0 are available. These have been
developed to cover specific needs as per data model changes in that
release.

.. automodule:: openupgrade_80
   :members:

