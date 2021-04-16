When you add a new migration script for a module, please
update the file ``ROADMAP.rst`` (same folder) to mark the module as migrated.

Possible values :

* ``Nothing to do`` : if your analysis concluded that there was nothing to do,
  or that everything was handled natively by the ORM.

* ``Partial``: if your scripts doesn't cover all the migration.

* ``Done (tentative)`` : if you consider your script as experimental.

* ``Done`` : if you consider the migration as complete.

* ``Done. Renamed from xxx``: if your analysis concluded that the addition of
  the module was because the module has been renamed.

* ``Done. Renamed to xxx``: if your analysis concluded that the deletion of
  the module was because the module has been renamed.

* ``Done. Merged in xxx``: if your analysis concluded that the deletion of
  the module was because the features (views, models, ...) has moved into another modules.

* ``Moved to OCA [#xxx]_``: if the features has been removed from Odoo,
  but are now available in the OCA.
