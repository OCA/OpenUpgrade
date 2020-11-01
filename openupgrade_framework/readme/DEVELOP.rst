This module contains two folders:


odoo_patch
----------

This folder contains python files, that correspond to python files present
in the folder ``odoo`` of the Odoo project.

it contains a lot of monkey patches, to make working an upgrade
between two major versions.
To see the patches added, you can use ``meld`` tools:

``meld PATH_TO_ODOO_FOLDER/odoo/ PATH_TO_OPENUPGRADE_FRAMEWORK_MODULE/odoo_patch``


To make more easy the diff analysis :

* Make sure the python files has the same path as the original one.

* Keep the same indentation as the original file. (using ``if True:`` if required)

* Add the following two lines at the beginning of your file, to avoid flake8 / pylint
  errors

.. code-block:: python

    # flake8: noqa
    # pylint: skip-file

* When you want to change the code. add the following tags:

    * For an addition:

.. code-block:: python

    # <OpenUpgrade:ADD>
    some code...
    # </OpenUpgrade>

    * For a change:

.. code-block:: python

    # <OpenUpgrade:CHANGE>
    some code...
    # </OpenUpgrade>

    * For a removal:

.. code-block:: python

    # <OpenUpgrade:REMOVE>
    # Comment the code, instead of removing it.
    # </OpenUpgrade>

openupgrade
-----------

Contains extra functions, called by the patches introduced in the first folder.
