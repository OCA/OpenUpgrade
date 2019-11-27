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
      this field, if it is encoded in the model, or any value that you might see
      fit (see the openupgrade library
      function :meth:`~openupgrade.set_defaults`). If any empty values remain,
      these can be reported by the openupgrade report module (TODO).
      If the field is a function field after the upgrade, this changes the cause
      for action. See below.

    * A field is now a function or a related field. This might or might not call
      for any action of your upgrade script, as the value is now automatically
      determined. At the same time, this might cause data loss. An example is
      the field employee's manager (hr module), which in Odoo 6 is derived
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
      field in Odoo 6, and the partner's title which as a selection (thus
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

    * A new model is introduced. Copy all access data from the access csv and
      security rules xml files and load them in your script. Also copy any
      other data that may be introduced in this release of Odoo. This may
      have consequences for other modules' migration scripts. TODO: create an
      overview of new or renamed modules.

The final section of the database layout analysis contains a simple report on
the changes that were detected.
