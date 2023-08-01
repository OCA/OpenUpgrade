Format Value Changing
+++++++++++++++++++++

Example
-------

From version 14.0 to version 15.0, the field ``description`` of the model ``hr.job``
has changed type from ``fields.Text`` to ``fields.Html``.

Source Code Differences
-----------------------

Version 14.0
""""""""""""

.. code-block:: python

    class HrJob(models.Model):
        _name = "hr.job"

        description = fields.Text(string='Job Description')

See `Full v14 Code Source <https://github.com/odoo/odoo/blob/f71626fa6ba413625d7242f5e13d05b8b95be48c/addons/hr/models/hr_job.py#L23>`_.


Version 15.0
""""""""""""

.. code-block:: python

    class HrJob(models.Model):
        _name = "hr.job"

        description = fields.Html(string='Job Description')


See `Full v15 Code Source <https://github.com/odoo/odoo/blob/ca7400f22258706f3d989c2008062648050b5b50/addons/hr/models/hr_job.py#L26>`_.


Analysis
--------

.. code-block:: text

    ...
    ---Fields in module 'hr'---
    ...
    hr      / hr.job        / description (text)        : type is now 'html' ('text')


See `Full V15 Analysis File <https://github.com/OCA/OpenUpgrade/blob/25866337eb463541a1e8f35180a1b721dcb061c0/openupgrade_scripts/scripts/hr/15.0.1.1/upgrade_analysis.txt#L20>`_.

Result without migration script / Expected Result
-------------------------------------------------

V14 table ``hr_job``
""""""""""""""""""""

.. csv-table::
   :header: "id", "name", "description"

   "50", "OpenUpgrade Expert", "the candidate must have read the documentation at this url : \\n\\n https://oca.github.io/OpenUpgrade"


V15 table ``hr_job`` (Without openupgrade)
""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "name", "description"

   "50", "OpenUpgrade Expert", "the candidate must have read the documentation at this url : \\n\\n https://oca.github.io/OpenUpgrade"


**Problem**:

The data has not been converted in HTML.

V15 table ``hr_job`` (With openupgrade)
"""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "name", "description"

   "50", "OpenUpgrade Expert", "<p>the candidate must have read the documentation at this url : </p><p><a href=""https://oca.github.io/OpenUpgrade/"" target=""_blank"" rel=""noreferrer noopener"">https://oca.github.io/OpenUpgrade/</a></p>"

Contribution to OpenUpgrade
---------------------------

Update ``upgrade_analysis_work.txt`` file
"""""""""""""""""""""""""""""""""""""""""

Add a comment after the line:

.. code-block:: text

    hr      / hr.job        / description (text)        : type is now 'html' ('text')
    # DONE pre-migration: convert to html


See `Full v15 Work Analysis File <https://github.com/OCA/OpenUpgrade/blob/25866337eb463541a1e8f35180a1b721dcb061c0/openupgrade_scripts/scripts/hr/15.0.1.1/upgrade_analysis_work.txt#L34-L35>`_.

Write migration Script
""""""""""""""""""""""

in the ``pre-migration.py`` script add:

.. code-block:: python

    from openupgradelib import openupgrade


    @openupgrade.migrate()
    def migrate(env, version):
        openupgrade.convert_field_to_html(env.cr, "hr_job", "description", "description")

See `Full V15 pre migration Script <https://github.com/OCA/OpenUpgrade/blob/15.0/openupgrade_scripts/scripts/hr/15.0.1.1/pre-migration.py>`_.


Notes
-----

* To be rigorous, the change must be made in the pre-migration section.

* There are several other functions that handle field type changes:

    * **date_to_datetime_tz** : to transform a ``field.Date()`` into a ``field.Datetime()``,
      with correct timezone management.
      (otherwise, all datetimes will have a number of offset hours,
      corresponding to the difference between the administrator's timezone and greenwitch's timezone
      at the time of migration)

    * **float_to_integer** : to transform a ``field.Float()`` into a ``field.Integer()``,
      truncating the decimal value.
      (If not done, the value will be rounded by odoo ORM)

    * **m2o_to_x2m** : to transform a ``field.Many2one()`` into a ``field.Many2many()``
      or ``field.One2many()``.
