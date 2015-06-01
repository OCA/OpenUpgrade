Test SQL Constraint Duplicate Remover
=====================================

This module tests the OpenUpgrade function remove_sql_constraint_duplicates

The function allows to eliminate every duplicate record of any model
given the list of attributes that form the unique sql constraint.

Every record in the database of any model that refers to a removed duplicate
will refer instead to the proper unique record that was kept.

Credits
=======

Contributors
------------

* David Dufresne <david.dufresne@savoirfairelinux.com>

Maintainer
----------

This module is maintained by the OpenUpgrade Community.
