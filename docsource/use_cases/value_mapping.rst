Value Mapping
+++++++++++++

From version 14.0 to version 15.0, in the module ``rating``, the options
available for the field ``rating_text`` (model ``rating.rating``) has been changed.


Source Code Differences
-----------------------

Version 14.0
""""""""""""

.. code-block:: python

    class Rating(models.Model):
        _name = "rating.rating"

    rating_text = fields.Selection(
        string='Rating',
        selection=[
            ('satisfied', 'Satisfied'),
            ('not_satisfied', 'Not satisfied'),
            ('highly_dissatisfied', 'Highly dissatisfied'),
            ('no_rating', 'No Rating yet'),
        ]
    )


See `Full V14 Code Source <https://github.com/odoo/odoo/blob/da9b89ad2697df7492e3f41c35f46c0b29afaef5/addons/rating/models/rating.py#L57>`_.


Version 15.0
""""""""""""

.. code-block:: python

    class Rating(models.Model):
        _name = "rating.rating"

    rating_text = fields.Selection(
        string='Rating',
        selection=[
            ('top', 'Satisfied'),
            ('ok', 'Okay'),
            ('ko', 'Dissatisfied'),
            ('none', 'No Rating yet'),
        ]
    )

See `Full V15 Code Source <https://github.com/odoo/odoo/blob/351b4e4b69629624158bad590c39e7930b6ae75f/addons/rating/models/rating.py#L58>`_.

Analysis
--------

.. code-block:: text

    ---Fields in module 'rating'---
    rating       / rating.rating            / rating_text (selection)       :
    selection_keys is now '['ko', 'none', 'ok', 'top']'
    ('['highly_dissatisfied', 'no_rating', 'not_satisfied', 'satisfied']')

See `Full V15 Analysis File <https://github.com/OCA/OpenUpgrade/blob/0d918b5b5dfb3125a5d881c8ccf4237997d8c7f5/openupgrade_scripts/scripts/rating/15.0.1.0/upgrade_analysis.txt#L1>`_.

Result without migration script / Expected Result
-------------------------------------------------

V14 table ``rating_rating``
"""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "res_id", "res_model", "rating", "rating_text"

   "1", "3", "project.task", "5", "satisfied"
   "2", "22", "project.task", "1", "highly_dissatisfied"
   "3", "4", "project.task", "5", "satisfied"
   "4", "2", "project.task", "1", "highly_dissatisfied"

V15 table rating_rating (Without migration script)
""""""""""""""""""""""""""""""""""""""""""""""""""

same table as in version 14.

**Problem**:

The old value does not correspond to anything in the new version
and is therefore no longer displayed in the interface.

.. image:: ./images/value-mapping-error.png

V15 table mail_activity_type (With migration script)
""""""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "res_id", "res_model", "rating", "rating_text", "openupgrade_legacy_14_0_rating_text"

   "1", "3", "project.task", "5", "top", "satisfied"
   "2", "22", "project.task", "1", "ko", "highly_dissatisfied"
   "3", "4", "project.task", "5", "top", "satisfied"
   "4", "2", "project.task", "1", "ko", "highly_dissatisfied"

Contribution to OpenUpgrade
---------------------------

Update ``upgrade_analysis_work.txt`` file
"""""""""""""""""""""""""""""""""""""""""

* Mention the operation performed, starting with ``# DONE:``

.. code-block:: text

    ---Fields in module 'rating'---
    rating       / rating.rating            / rating_text (selection)       :
    selection_keys is now '['ko', 'none', 'ok', 'top']'
    ('['highly_dissatisfied', 'no_rating', 'not_satisfied', 'satisfied']')
    # DONE: post-migration: mapped value from old keys to new keys

See `Full V15 Work Analysis File <https://github.com/OCA/OpenUpgrade/blob/0d918b5b5dfb3125a5d881c8ccf4237997d8c7f5/openupgrade_scripts/scripts/rating/15.0.1.0/upgrade_analysis_work.txt#L3>`_.

Write migration Script
""""""""""""""""""""""

In the ``pre-migration.py`` script add:

.. code-block:: python

    from openupgradelib import openupgrade

    @openupgrade.migrate()
    def migrate(env, version):
        openupgrade.copy_columns(
            env.cr,
            {"rating_rating": [("rating_text", None, None)]},
        )

In the ``post-migration.py`` script add:

.. code-block:: python

    from openupgradelib import openupgrade

    @openupgrade.migrate()
    def migrate(env, version):
        openupgrade.map_values(
            env.cr,
            openupgrade.get_legacy_name("rating_text"),
            "rating_text",
            [
                ("satisfied", "top"),
                ("not satisfied", "ok"),
                ("highly_dissatisfied", "ko"),
                ("no_rating", "none"),
            ],
            table="rating_rating",
        )


See `Full pre migration Script <https://github.com/OCA/OpenUpgrade/blob/0d918b5b5dfb3125a5d881c8ccf4237997d8c7f5/openupgrade_scripts/scripts/rating/15.0.1.0/post-migration.py#L1>`_.


Notes
-----

* Sometimes, there is a loss of information.
  that is the case in the above example:
  Some mapping are correct:

    * ``satisfied`` -> ``top``
    * ``highly_dissatisfied`` -> ``ko``
    * ``no_rating`` -> ``none``

  But the last mapping is ``not satisfied`` -> ``ok``, which changes the semantics of the data.
  It is not always possible to do otherwise and the developer must make the best suited choices.

* Sometimes, there is nothing to do.
  This is the case, when there are just one or more new options available in the recent version
  AND when no option is disappeared.

* the old data is kept in the column whose name starts with ``openupgrade_legacy_``.
  This allows you to check that everything is correct after the migration,
  and to make any custom fixes.
  Once this is done, you can delete this data.
  (See: :doc:`../after_migration`)