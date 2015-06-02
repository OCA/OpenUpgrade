# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2011-2013 Therp BV (<http://therp.nl>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os
import inspect
import logging
from openerp import release, osv, tools, SUPERUSER_ID
from openerp.modules.registry import RegistryManager
import openupgrade_tools
from itertools import groupby
from operator import attrgetter

# The server log level has not been set at this point
# so to log at loglevel debug we need to set it
# manually here. As a consequence, DEBUG messages from
# this file are always logged
logger = logging.getLogger('OpenUpgrade')
logger.setLevel(logging.DEBUG)

__all__ = [
    'migrate',
    'load_data',
    'rename_columns',
    'rename_tables',
    'rename_models',
    'rename_xmlids',
    'drop_columns',
    'delete_model_workflow',
    'update_workflow_workitems',
    'warn_possible_dataloss',
    'set_defaults',
    'logged_query',
    'column_exists',
    'table_exists',
    'update_module_names',
    'add_ir_model_fields',
    'get_legacy_name',
    'm2o_to_m2m',
    'message',
    'deactivate_workflow_transitions',
    'reactivate_workflow_transitions',
    'remove_sql_constraint_duplicates',
]


def load_data(cr, module_name, filename, idref=None, mode='init'):
    """
    Load an xml or csv data file from your post script. The usual case for \
    this is the occurrence of newly added essential or useful data in the \
    module that is marked with "noupdate='1'" and without "forcecreate='1'" \
    so that it will not be loaded by the usual upgrade mechanism. Leaving \
    the 'mode' argument to its default 'init' will load the data from your \
    migration script.

    Theoretically, you could simply load a stock file from the module, but be
    careful not to reinitialize any data that could have been customized.
    Preferably, select only the newly added items. Copy these to a file
    in your migrations directory and load that file.
    Leave it to the user to actually delete existing resources that are
    marked with 'noupdate' (other named items will be deleted
    automatically).


    :param module_name: the name of the module
    :param filename: the path to the filename, relative to the module \
    directory.
    :param idref: optional hash with ?id mapping cache?
    :param mode: one of 'init', 'update', 'demo'. Always use 'init' for \
    adding new items from files that are marked with 'noupdate'. Defaults to \
    'init'.
    """

    if idref is None:
        idref = {}
    logger.info('%s: loading %s' % (module_name, filename))
    _, ext = os.path.splitext(filename)
    pathname = os.path.join(module_name, filename)
    fp = tools.file_open(pathname)
    try:
        if ext == '.csv':
            noupdate = True
            tools.convert_csv_import(
                cr, module_name, pathname, fp.read(), idref, mode, noupdate)
        else:
            tools.convert_xml_import(cr, module_name, fp, idref, mode=mode)
    finally:
        fp.close()

# for backwards compatibility
load_xml = load_data
table_exists = openupgrade_tools.table_exists


def rename_columns(cr, column_spec):
    """
    Rename table columns. Typically called in the pre script.

    :param column_spec: a hash with table keys, with lists of tuples as \
    values. Tuples consist of (old_name, new_name). Use None for new_name \
    to trigger a conversion of old_name using get_legacy_name()
    """
    for table in column_spec.keys():
        for (old, new) in column_spec[table]:
            if new is None:
                new = get_legacy_name(old)
            logger.info("table %s, column %s: renaming to %s",
                        table, old, new)
            cr.execute('ALTER TABLE "%s" RENAME "%s" TO "%s"' %
                       (table, old, new,))
            cr.execute('DROP INDEX IF EXISTS "%s_%s_index"' % (table, old))


def rename_tables(cr, table_spec):
    """
    Rename tables. Typically called in the pre script.
    This function also renames the id sequence if it exists and if it is
    not modified in the same run.

    :param table_spec: a list of tuples (old table name, new table name).

    """
    # Append id sequences
    to_rename = [x[0] for x in table_spec]
    for old, new in list(table_spec):
        if (table_exists(cr, old + '_id_seq') and
                old + '_id_seq' not in to_rename):
            table_spec.append((old + '_id_seq', new + '_id_seq'))
    for (old, new) in table_spec:
        logger.info("table %s: renaming to %s",
                    old, new)
        cr.execute('ALTER TABLE "%s" RENAME TO "%s"' % (old, new,))


def rename_models(cr, model_spec):
    """
    Rename models. Typically called in the pre script.
    :param model_spec: a list of tuples (old model name, new model name).

    Use case: if a model changes name, but still implements equivalent
    functionality you will want to update references in for instance
    relation fields.

    """
    for (old, new) in model_spec:
        logger.info("model %s: renaming to %s",
                    old, new)
        cr.execute('UPDATE ir_model SET model = %s '
                   'WHERE model = %s', (new, old,))
        cr.execute('UPDATE ir_model_fields SET relation = %s '
                   'WHERE relation = %s', (new, old,))
        cr.execute('UPDATE ir_model_data SET model = %s '
                   'WHERE model = %s', (new, old,))
    # TODO: signal where the model occurs in references to ir_model


def rename_xmlids(cr, xmlids_spec):
    """
    Rename XML IDs. Typically called in the pre script.
    One usage example is when an ID changes module. In OpenERP 6 for example,
    a number of res_groups IDs moved to module base from other modules (
    although they were still being defined in their respective module).
    """
    for (old, new) in xmlids_spec:
        if '.' not in old or '.' not in new:
            logger.error(
                'Cannot rename XMLID %s to %s: need the module '
                'reference to be specified in the IDs' % (old, new))
        else:
            query = ("UPDATE ir_model_data SET module = %s, name = %s "
                     "WHERE module = %s and name = %s")
            logged_query(cr, query, tuple(new.split('.') + old.split('.')))


def drop_columns(cr, column_spec):
    """
    Drop columns but perform an additional check if a column exists.
    This covers the case of function fields that may or may not be stored.
    Consider that this may not be obvious: an additional module can govern
    a function fields' store properties.

    :param column_spec: a list of (table, column) tuples
    """
    for (table, column) in column_spec:
        logger.info("table %s: drop column %s",
                    table, column)
        if column_exists(cr, table, column):
            cr.execute('ALTER TABLE "%s" DROP COLUMN "%s"' %
                       (table, column))
        else:
            logger.warn("table %s: column %s did not exist",
                        table, column)


def update_workflow_workitems(cr, pool, ref_spec_actions):
    """Find all the workflow items from the target state to set them to
    the wanted state.

    When a workflow action is removed, from model, the objects whose states
    are in these actions need to be set to another to be able to continue the
    workflow properly.

    Run in pre-migration

    :param ref_spec_actions: list of tuples with couple of workflow.action's
        external ids. The first id is replaced with the second.
    :return: None

    .. versionadded:: 7.0
    """
    workflow_workitems = pool['workflow.workitem']
    ir_model_data_model = pool['ir.model.data']

    for (target_external_id, fallback_external_id) in ref_spec_actions:
        target_activity = ir_model_data_model.get_object(
            cr, SUPERUSER_ID,
            target_external_id.split(".")[0],
            target_external_id.split(".")[1],
        )
        fallback_activity = ir_model_data_model.get_object(
            cr, SUPERUSER_ID,
            fallback_external_id.split(".")[0],
            fallback_external_id.split(".")[1],
        )
        ids = workflow_workitems.search(
            cr, SUPERUSER_ID, [('act_id', '=', target_activity.id)]
        )
        if ids:
            logger.info(
                "Moving %d items in the removed workflow action (%s) to a "
                "fallback action (%s): %s",
                len(ids), target_activity.name, fallback_activity.name, ids
            )
            workflow_workitems.write(
                cr, SUPERUSER_ID, ids, {'act_id': fallback_activity.id}
            )


def delete_model_workflow(cr, model):
    """
    Forcefully remove active workflows for obsolete models,
    to prevent foreign key issues when the orm deletes the model.
    """
    logged_query(
        cr,
        "DELETE FROM wkf_workitem WHERE act_id in "
        "( SELECT wkf_activity.id "
        "  FROM wkf_activity, wkf "
        "  WHERE wkf_id = wkf.id AND "
        "  wkf.osv = %s"
        ")", (model,))
    logged_query(
        cr,
        "DELETE FROM wkf WHERE osv = %s", (model,))


def warn_possible_dataloss(cr, pool, old_module, fields):
    """
    Use that function in the following case:
    if a field of a model was moved from a 'A' module to a 'B' module.
    ('B' depend on 'A'),
    This function will test if 'B' is installed.
    If not, count the number of different value and possibly warn the user.
    Use orm, so call from the post script.

    :param old_module: name of the old module
    :param fields: list of dictionary with the following keys:
        'table' : name of the table where the field is.
        'field' : name of the field that are moving.
        'new_module' : name of the new module.

    .. versionadded:: 7.0
    """
    module_obj = pool.get('ir.module.module')
    for field in fields:
        module_ids = module_obj.search(cr, SUPERUSER_ID, [
            ('name', '=', field['new_module']),
            ('state', 'in', ['installed', 'to upgrade', 'to install'])
        ])
        if not module_ids:
            cr.execute(
                "SELECT count(*) FROM (SELECT %s from %s group by %s) "
                "as tmp" % (
                    field['field'], field['table'], field['field']))
            row = cr.fetchone()
            if row[0] == 1:
                # not a problem, that field wasn't used.
                # Just a loss of functionality
                logger.info(
                    "Field '%s' from module '%s' was moved to module "
                    "'%s' which is not installed: "
                    "No dataloss detected, only loss of functionality"
                    % (field['field'], old_module, field['new_module']))
            else:
                # there is data loss after the migration.
                message(
                    cr, old_module,
                    "Field '%s' was moved to module "
                    "'%s' which is not installed: "
                    "There were %s distinct values in this field.",
                    field['field'], field['new_module'], row[0])


def set_defaults(cr, pool, default_spec, force=False):
    """
    Set default value. Useful for fields that are newly required. Uses orm, so
    call from the post script.

    :param default_spec: a hash with model names as keys. Values are lists of \
    tuples (field, value). None as a value has a special meaning: it assigns \
    the default value. If this value is provided by a function, the function \
    is called as the user that created the resource.
    :param force: overwrite existing values. To be used for assigning a non- \
    default value (presumably in the case of a new column). The ORM assigns \
    the default value as declared in the model in an earlier stage of the \
    process. Beware of issues with resources loaded from new data that \
    actually do require the model's default, in combination with the post \
    script possible being run multiple times.
    """

    def write_value(ids, field, value):
        logger.debug(
            "model %s, field %s: setting default value of resources %s to %s",
            model, field, ids, unicode(value))
        for res_id in ids:
            # Iterating over ids here as a workaround for lp:1131653
            obj.write(cr, SUPERUSER_ID, [res_id], {field: value})

    for model in default_spec.keys():
        obj = pool.get(model)
        if not obj:
            raise osv.except_osv(
                "Migration: error setting default, no such model: %s" %
                model, "")

        for field, value in default_spec[model]:
            domain = not force and [(field, '=', False)] or []
            ids = obj.search(cr, SUPERUSER_ID, domain)
            if not ids:
                continue
            if value is not None:
                write_value(ids, field, value)
                continue
            # So value is None.
            # Set the value by calling the _defaults of the object.
            # Typically used for company_id on various models, and in that
            # case the result depends on the user associated with the
            # object. We retrieve create_uid for this purpose and need to
            # call the _defaults function per resource. Otherwise, write
            # all resources at once.
            if field in obj._defaults:
                if not callable(obj._defaults[field]):
                    write_value(ids, field, obj._defaults[field])
                else:
                    cr.execute(
                        "SELECT id, COALESCE(create_uid, 1) FROM %s " %
                        obj._table + "WHERE id in %s", (tuple(ids),))
                    # Execute the function once per user_id
                    user_id_map = {}
                    for row in cr.fetchall():
                        user_id_map.setdefault(row[1], []).append(row[0])
                    for user_id in user_id_map:
                        write_value(
                            user_id_map[user_id], field,
                            obj._defaults[field](obj, cr, user_id, None))
            else:
                error = (
                    "OpenUpgrade: error setting default, field %s with "
                    "None default value not in %s' _defaults" % (
                        field, model))
                logger.error(error)
                # this exeption seems to get lost in a higher up try block
                osv.except_osv("OpenUpgrade", error)


def logged_query(cr, query, args=None):
    """
    Logs query and affected rows at level DEBUG
    """
    if args is None:
        args = []
    logger.debug('Running %s', query % tuple(args))
    cr.execute(query, args)
    logger.debug('%s rows affected', cr.rowcount)
    return cr.rowcount


def column_exists(cr, table, column):
    """ Check whether a certain column exists """
    cr.execute(
        'SELECT count(attname) FROM pg_attribute '
        'WHERE attrelid = '
        '( SELECT oid FROM pg_class WHERE relname = %s ) '
        'AND attname = %s',
        (table, column))
    return cr.fetchone()[0] == 1


def update_module_names(cr, namespec):
    """
    Deal with changed module names of certified modules
    in order to prevent  'certificate not unique' error,
    as well as updating the module reference in the
    XML id.

    :param namespec: tuple of (old name, new name)
    """
    for (old_name, new_name) in namespec:
        query = ("UPDATE ir_module_module SET name = %s "
                 "WHERE name = %s")
        logged_query(cr, query, (new_name, old_name))
        query = ("UPDATE ir_model_data SET module = %s "
                 "WHERE module = %s ")
        logged_query(cr, query, (new_name, old_name))
        query = ("UPDATE ir_model_data SET name = %s "
                 "WHERE name = %s AND module = 'base' AND "
                 "model='ir.module.module' ")
        logged_query(cr, query,
                     ("module_%s" % new_name, "module_%s" % old_name))
        query = ("UPDATE ir_module_module_dependency SET name = %s "
                 "WHERE name = %s")
        logged_query(cr, query, (new_name, old_name))


def add_ir_model_fields(cr, columnspec):
    """
    Typically, new columns on ir_model_fields need to be added in a very
    early stage in the upgrade process of the base module, in raw sql
    as they need to be in place before any model gets initialized.
    Do not use for fields with additional SQL constraints, such as a
    reference to another table or the cascade constraint, but craft your
    own statement taking them into account.

    :param columnspec: tuple of (column name, column type)
    """
    for column in columnspec:
        query = 'ALTER TABLE ir_model_fields ADD COLUMN %s %s' % (
            column)
        logged_query(cr, query, [])


def get_legacy_name(original_name):
    """
    Returns a versioned name for legacy tables/columns/etc
    Use this function instead of some custom name to avoid
    collisions with future or past legacy tables/columns/etc

    :param original_name: the original name of the column
    :param version: current version as passed to migrate()
    """
    return 'openupgrade_legacy_' + ('_').join(
        map(str, release.version_info[0:2])) + '_' + original_name


def m2o_to_m2m(cr, model, table, field, source_field):
    """
    Recreate relations in many2many fields that were formerly
    many2one fields. Use rename_columns in your pre-migrate
    script to retain the column's old value, then call m2o_to_m2m
    in your post-migrate script.

    :param model: The target model pool object
    :param table: The source table
    :param field: The field name of the target model
    :param source_field: the many2one column on the source table.

    .. versionadded:: 7.0
    """
    if not model._columns.get(field):
        raise osv.except_osv(
            "Error", "m2o_to_m2m: field %s doesn't exist in model %s" % (
                field, model._name))
    if not isinstance(model._columns[field], osv.fields.many2many):
        raise osv.except_osv(
            "Error", "m2o_to_m2m: field %s of model %s is not a many2many "
                     "one" % (field, model._name))
    rel, id1, id2 = osv.fields.many2many._sql_names(model._columns[field],
                                                    model)
    logged_query(
        cr,
        "INSERT INTO %s (%s, %s) "
        "    SELECT id, %s "
        "    FROM %s "
        "    WHERE %s is not null" %
        (rel, id1, id2, source_field, table, source_field))


def message(cr, module, table, column,
            message, *args, **kwargs):
    """
    Log handler for non-critical notifications about the upgrade.
    To be extended with logging to a table for reporting purposes.

    :param module: the module name that the message concerns
    :param table: the model that this message concerns (may be False, \
    but preferably not if 'column' is defined)
    :param column: the column that this message concerns (may be False)

    .. versionadded:: 7.0
    """
    argslist = list(args or [])
    prefix = ': '
    if column:
        argslist.insert(0, column)
        prefix = ', column %s' + prefix
    if table:
        argslist.insert(0, table)
        prefix = ', table %s' + prefix
    argslist.insert(0, module)
    prefix = 'Module %s' + prefix

    logger.warn(prefix + message, *argslist, **kwargs)


def deactivate_workflow_transitions(cr, model, transitions=None):
    """
    Disable workflow transitions for workflows on a given model.
    This can be necessary for automatic workflow transitions when writing
    to an object via the ORM in the post migration step.

    Returns a dictionary to be used on reactivate_workflow_transitions

    :param model: the model for which workflow transitions should be
    deactivated
    :param transitions: a list of ('module', 'name') xmlid tuples of
    transitions to be deactivated. Don't pass this if there's no specific
    reason to do so, the default is to deactivate all transitions

    .. versionadded:: 7.0
    """
    transition_ids = []
    if transitions:
        data_obj = RegistryManager.get(cr.dbname)['ir.model.data']
        for module, name in transitions:
            try:
                transition_ids.append(
                    data_obj.get_object_reference(
                        cr, SUPERUSER_ID, module, name)[1])
            except ValueError:
                continue
    else:
        cr.execute(
            '''select distinct t.id
            from wkf w
            join wkf_activity a on a.wkf_id=w.id
            join wkf_transition t
                on t.act_from=a.id or t.act_to=a.id
            where w.osv=%s''', (model,))
        transition_ids = [i for i, in cr.fetchall()]
    cr.execute(
        'select id, condition from wkf_transition where id in %s',
        (tuple(transition_ids),))
    transition_conditions = dict(cr.fetchall())
    cr.execute(
        "update wkf_transition set condition = 'False' WHERE id in %s",
        (tuple(transition_ids),))
    return transition_conditions


def reactivate_workflow_transitions(cr, transition_conditions):
    """
    Reactivate workflow transition previously deactivated by
    deactivate_workflow_transitions.

    :param transition_conditions: a dictionary returned by
    deactivate_workflow_transitions

    .. versionadded:: 7.0
    """
    for transition_id, condition in transition_conditions.iteritems():
        cr.execute(
            'update wkf_transition set condition = %s where id = %s',
            (condition, transition_id))


def migrate():
    """
    This is the decorator for the migrate() function
    in migration scripts.
    Return when the 'version' argument is not defined,
    and log execeptions.
    Retrieve debug context data from the frame above for
    logging purposes.
    """
    def wrap(func):
        def wrapped_function(cr, version):
            stage = 'unknown'
            module = 'unknown'
            filename = 'unknown'
            try:
                frame = inspect.getargvalues(inspect.stack()[1][0])
                stage = frame.locals['stage']
                module = frame.locals['pkg'].name
                filename = frame.locals['fp'].name
            except Exception, e:
                logger.error(
                    "'migrate' decorator: failed to inspect "
                    "the frame above: %s" % e)
                pass
            if not version:
                return
            logger.info(
                "%s: %s-migration script called with version %s" %
                (module, stage, version))
            try:
                # The actual function is called here
                func(cr, version)
            except Exception, e:
                logger.error(
                    "%s: error in migration script %s: %s" %
                    (module, filename, str(e).decode('utf8')))
                logger.exception(e)
                raise
        return wrapped_function
    return wrap


def remove_sql_constraint_duplicates(cr, model, constraint_attrs):
    """
    Remove all duplicates after a sql constraint is applied on a model.

    For every field many2one and many2many with the given model as relation,
    change the duplicate ids with the id of the record kept.

    This method must be called in post-migration so that the model being
    edited can be accessed through the orm.

    When upgrading the module, if there are duplicates, integrity errors
    will be raised before the method is run but this will not prevent
    the method from running.

    Use with care, this method will keep one record for each set of duplicates
    and it might keep the wrong record.

    :param model: the model on which the constraint is applied
    :param constraint_attrs: a list of strings containing the fields that
                                form the uniq key
    """
    pool = RegistryManager.get(cr.dbname)
    model_pool = pool[model]
    model_table = model_pool._table

    # Get all fields with the given model as many2one relation
    field_pool = pool['ir.model.fields']
    field_m2o_ids = field_pool.search(cr, SUPERUSER_ID, [
        ('relation', '=', model),
        ('ttype', '=', 'many2one'),
    ])
    # List of tables where to look for duplicates
    # This is trivial for many2one relations
    tables_to_lookup = [
        (
            pool[field.model_id.model]._table,
            field.name, 'many2one'
        ) for field in field_pool.browse(cr, SUPERUSER_ID, field_m2o_ids)
    ]

    # For many2many relations, we need to check over the existing
    # foreign keys in the database in order to find the tables

    # Get all fields with the given model as many2many relation
    field_m2m_ids = field_pool.search(cr, SUPERUSER_ID, [
        ('relation', '=', model),
        ('ttype', '=', 'many2many'),
    ])
    fields_m2m = field_pool.browse(cr, SUPERUSER_ID, field_m2m_ids)

    for field in fields_m2m:

        other_model_table = pool[field.model_id.model]._table

        # Get all primary key constraints for the given table
        query = "SELECT " \
            "    tc.table_name, kcu.column_name, ccu.table_name " \
            "FROM " \
            "    information_schema.table_constraints AS tc " \
            "    JOIN information_schema.key_column_usage AS kcu " \
            "        ON tc.constraint_name = kcu.constraint_name " \
            "    JOIN information_schema.constraint_column_usage AS ccu " \
            "        ON ccu.constraint_name = tc.constraint_name " \
            "WHERE constraint_type = 'FOREIGN KEY' " \
            "        and ccu.table_name " \
            "        in ('%(model_table)s', '%(other_model_table)s') " \
            " ORDER BY tc.table_name;" % {
                'model_table': model_table,
                'other_model_table': other_model_table
            }

        cr.execute(query)
        for key, group in groupby(cr.fetchall(), key=lambda c: c[0]):
            constraints = list(group)

            model_field = next(
                (c[1] for c in constraints if c[2] == model_table), False)
            other_field = next(
                (c[1] for c in constraints if c[2] == other_model_table), False
            )

            if model_field and other_field:
                # Add the current table to the list of tables where to look
                # for duplicates
                tables_to_lookup.append((
                    key, model_field, 'many2many', other_field))

    # Get all records
    record_ids = model_pool.search(cr, SUPERUSER_ID, [])
    records = model_pool.browse(cr, SUPERUSER_ID, record_ids)

    # Sort records by the constraint attributes
    # so that they can be grouped with itertools.groupby
    records.sort(key=attrgetter(*constraint_attrs))

    for key, group in groupby(records, key=lambda x: tuple(
        x[attr] for attr in constraint_attrs)
    ):
        grouped_records = list(group)

        if len(grouped_records) > 1:
            # Define a record to keep
            new_record_id = grouped_records[0].id

            # All other records are to remove
            old_record_ids = [z.id for z in grouped_records[1:]]

            all_record_ids = old_record_ids + [new_record_id]

            # Replace every many2one record in the database that has an old
            # record as value with the record to keep

            for table in tables_to_lookup:
                table_name = table[0]

                # Prevent the upgrade script to create duplicates
                # in the many2many relation table and raise a constraint error
                if table[2] == 'many2many':
                    cr.execute(
                        "   SELECT t.%(other_field)s, t.%(field_name)s "
                        "   FROM %(table_name)s as t"
                        "   WHERE %(field_name)s "
                        "   in %(all_record_ids)s "
                        "   ORDER BY %(other_field)s" %
                        {
                            'table_name': table_name,
                            'field_name': table[1],
                            'other_field': table[3],
                            'all_record_ids': tuple(all_record_ids),
                        })

                    for k, group_to_check in groupby(
                        cr.fetchall(), lambda rec: rec[0]
                    ):
                        group_to_check = list(group_to_check)
                        if len(group_to_check) > 1:
                            for rec_to_unlink in group_to_check[1:]:
                                cr.execute(
                                    "   DELETE FROM %(table_name)s "
                                    "   WHERE %(field_name)s = %(field_value)s"
                                    "   AND %(other_field)s "
                                    "   = %(other_field_value)s" %
                                    {
                                        'table_name': table_name,
                                        'field_name': table[1],
                                        'field_value': rec_to_unlink[1],
                                        'other_field': table[3],
                                        'other_field_value': rec_to_unlink[0],
                                    })

                # Main upgrade script
                cr.execute(
                    "   UPDATE %(table_name)s"
                    "   SET %(field_name)s = %(new_value)s"
                    "   WHERE %(field_name)s %(old_record_ids)s;" %
                    {
                        'table_name': table_name,
                        'field_name': table[1],
                        'new_value': new_record_id,
                        'old_record_ids': len(old_record_ids) > 1 and
                        'in %s' % (tuple(old_record_ids),) or '= %s' %
                        old_record_ids[0]
                    })

            logger.info('Unlinking the following ids from table %s: %s' % (
                model_table, old_record_ids))
            model_pool.unlink(cr, SUPERUSER_ID, old_record_ids)
