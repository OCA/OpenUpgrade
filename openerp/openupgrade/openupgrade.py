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
from openerp import release, tools, SUPERUSER_ID
from openerp.osv import orm
from openerp.tools.mail import plaintext2html
import openupgrade_tools

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
    'add_xmlid',
    'drop_columns',
    'delete_model_workflow',
    'warn_possible_dataloss',
    'set_defaults',
    'logged_query',
    'column_exists',
    'table_exists',
    'update_module_names',
    'add_ir_model_fields',
    'get_legacy_name',
    'm2o_to_x2m',
    'float_to_integer',
    'message',
    'check_values_selection_field',
    'move_field_m2o',
    'convert_field_to_html',
    'deactivate_workflow_transitions',
    'reactivate_workflow_transitions',
]


def check_values_selection_field(cr, table_name, field_name, allowed_values):
    """
        check if the field selection 'field_name' of the table 'table_name'
        has only the values 'allowed_values'.
        If not return False and log an error.
        If yes, return True.
    """
    res = True
    cr.execute("SELECT %s, count(*) FROM %s GROUP BY %s;" %
               (field_name, table_name, field_name))
    for row in cr.fetchall():
        if row[0] not in allowed_values:
            logger.error(
                "Invalid value '%s' in the table '%s' "
                "for the field '%s'. (%s rows).",
                row[0], table_name, field_name, row[1])
            res = False
    return res


def load_data(cr, module_name, filename, idref=None, mode='init'):
    """
    Load an xml or csv data file from your post script. The usual case for
    this is the
    occurrence of newly added essential or useful data in the module that is
    marked with "noupdate='1'" and without "forcecreate='1'" so that it will
    not be loaded by the usual upgrade mechanism. Leaving the 'mode' argument
    to its default 'init' will load the data from your migration script.

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
    :param mode: one of 'init', 'update', 'demo'. Always use 'init' \
    for adding new items from files that are marked with 'noupdate'. Defaults \
    to 'init'.
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
            cr.execute(
                'ALTER TABLE "%s" RENAME "%s" TO "%s"' % (table, old, new,))
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
        if not old.split('.') or not new.split('.'):
            logger.error(
                'Cannot rename XMLID %s to %s: need the module '
                'reference to be specified in the IDs' % (old, new))
        else:
            query = ("UPDATE ir_model_data SET module = %s, name = %s "
                     "WHERE module = %s and name = %s")
            logged_query(cr, query, tuple(new.split('.') + old.split('.')))


def add_xmlid(cr, module, xmlid, model, res_id, noupdate=False):
    """
    Adds an entry in ir_model_data. Typically called in the pre script.
    One usage example is when an entry has been add in the XML and there is
    a high probability that the user has already created the entry manually.
    For example, a currency was added in the XML data of the base module
    in OpenERP 6 but the user had already created this missing currency
    by hand in it's 5.0 database. In order to avoid having 2 identical
    currencies (which is in fact blocked by an sql_constraint), you have to
    add the entry in ir_model_data before the upgrade.
    """
    # Check if the XMLID doesn't already exists
    cr.execute(
        "SELECT id FROM ir_model_data WHERE module=%s AND name=%s "
        "AND model=%s",
        (module, xmlid, model))
    already_exists = cr.fetchone()
    if already_exists:
        return False
    else:
        logged_query(
            cr,
            "INSERT INTO ir_model_data (create_uid, create_date, "
            "write_uid, write_date, date_init, date_update, noupdate, "
            "name, module, model, res_id) "
            "VALUES (%s, (now() at time zone 'UTC'), %s, "
            "(now() at time zone 'UTC'), (now() at time zone 'UTC'), "
            "(now() at time zone 'UTC'), %s, %s, %s, %s, %s)", (
                SUPERUSER_ID, SUPERUSER_ID, noupdate,
                xmlid, module, model, res_id))
        return True


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
        'new_module' : name of the new module

    .. versionadded:: 7.0
    """
    module_obj = pool.get('ir.module.module')
    for field in fields:
        module_ids = module_obj.search(
            cr, SUPERUSER_ID, [
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

    :param default_spec: a hash with model names as keys. Values are lists \
    of tuples (field, value). None as a value has a special meaning: it \
    assigns the default value. If this value is provided by a function, the \
    function is called as the user that created the resource.
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
            raise orm.except_orm(
                "Error",
                "Migration: error setting default, no such model: %s" % model)

        for field, value in default_spec[model]:
            domain = not force and [(field, '=', False)] or []
            ids = obj.search(cr, SUPERUSER_ID, domain)
            if not ids:
                continue
            if value is None:
                # Set the value by calling the _defaults of the object.
                # Typically used for company_id on various models, and in that
                # case the result depends on the user associated with the
                # object. We retrieve create_uid for this purpose and need to
                # call the defaults function per resource. Otherwise, write
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
                    orm.except_orm("OpenUpgrade", error)
            else:
                write_value(ids, field, value)


def logged_query(cr, query, args=None):
    """
    Logs query and affected rows at level DEBUG
    """
    if args is None:
        args = []
    cr.execute(query, args)
    logger.debug('Running %s', query % tuple(args))
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
    return 'openupgrade_legacy_'+('_').join(
        map(str, release.version_info[0:2]))+'_'+original_name


def m2o_to_x2m(cr, model, table, field, source_field):
    """
    Transform many2one relations into one2many or many2many.
    Use rename_columns in your pre-migrate
    script to retain the column's old value, then call m2o_to_x2m
    in your post-migrate script.

    :param model: The target model registry object
    :param table: The source table
    :param field: The new field name on the target model
    :param source_field: the (renamed) many2one column on the source table.

    .. versionadded:: 7.0
    """
    cr.execute('SELECT id, %(field)s '
               'FROM %(table)s '
               'WHERE %(field)s is not null' % {
                   'table': table,
                   'field': source_field,
                   })
    for row in cr.fetchall():
        model.write(cr, SUPERUSER_ID, row[0], {field: [(4, row[1])]})

# Backwards compatibility
m2o_to_m2m = m2o_to_x2m


def float_to_integer(cr, table, field):
    """
    Change column type from float to integer. It will just
    truncate the float value (It won't round it)

    :param table: The table
    :param field: The field name for which we want to change the type

    .. versionadded:: 8.0
    """
    logged_query(
        cr,
        "ALTER TABLE %(table)s "
        "ALTER COLUMN %(field)s "
        "TYPE integer" % {
            'table': table,
            'field': field,
            })


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


def migrate(no_version=False):
    """
    This is the decorator for the migrate() function
    in migration scripts.
    Set argument 'no_version' to True if the method as to be taken into account
    if the module is installed during a migration.
    Return when the 'version' argument is not defined and no_version is False,
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
            if not version and not no_version:
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


def move_field_m2o(
        cr, pool,
        registry_old_model, field_old_model, m2o_field_old_model,
        registry_new_model, field_new_model,
        quick_request=True, compute_func=None, binary_field=False):
    """
    Use that function in the following case:
    A field moves from a model A to the model B with : A -> m2o -> B.
    (For exemple product_product -> product_template)
    This function manage the migration of this field.
    available on post script migration.
    :param registry_old_model: registry of the model A;
    :param field_old_model: name of the field to move in model A;
    :param m2o_field_old_model: name of the field of the table of the model A;
        that link model A to model B;
    :param registry_new_model: registry of the model B;
    :param field_new_model: name of the field to move in model B;
    :param quick_request: Set to False, if you want to use write function to
        update value; Otherwise, the function will use UPDATE SQL request;
    :param compute_func: This a function that receives 4 parameters:
        cr, pool: common args;
        id: id of the instance of Model B
        vals:  list of different values.
        This function must return a unique value that will be set to the
        instance of Model B which id is 'id' param;
        If compute_func is not set, the algorithm will take the value that
        is the most present in vals.
    :binary_field: Set to True if the migrated field is a binary field
    .. versionadded:: 8.0
    """
    def default_func(cr, pool, id, vals):
        """This function return the value the most present in vals."""
        quantity = {}.fromkeys(set(vals), 0)
        for val in vals:
            quantity[val] += 1
        res = vals[0]
        for val in vals:
            if quantity[res] < quantity[val]:
                res = val
        return res

    table_old_model = pool[registry_old_model]._table
    table_new_model = pool[registry_new_model]._table
    # Manage regular case (all the value are identical)
    cr.execute(
        " SELECT %s"
        " FROM %s"
        " GROUP BY %s"
        " HAVING count(*) = 1;" % (
            m2o_field_old_model, table_old_model, m2o_field_old_model
        ))
    ok_ids = [x[0] for x in cr.fetchall()]
    if quick_request:
        query = (
            " UPDATE %s as new_table"
            " SET %s=("
            "    SELECT old_table.%s"
            "    FROM %s as old_table"
            "    WHERE old_table.%s=new_table.id"
            "    LIMIT 1) "
            " WHERE id in %%s" % (
                table_new_model, field_new_model, field_old_model,
                table_old_model, m2o_field_old_model))
        logged_query(cr, query, [tuple(ok_ids)])
    else:
        query = (
            " SELECT %s, %s"
            " FROM %s "
            " WHERE %s in %%s"
            " GROUP BY %s, %s" % (
                m2o_field_old_model, field_old_model, table_old_model,
                m2o_field_old_model, m2o_field_old_model, field_old_model))
        cr.execute(query, [tuple(ok_ids)])
        for res in cr.fetchall():
            if res[1] and binary_field:
                pool[registry_new_model].write(
                    cr, SUPERUSER_ID, res[0],
                    {field_new_model: res[1][:]})
            else:
                pool[registry_new_model].write(
                    cr, SUPERUSER_ID, res[0],
                    {field_new_model: res[1]})

    # Manage non-determinist case (some values are different)
    func = compute_func if compute_func else default_func
    cr.execute(
        " SELECT %s "
        " FROM %s "
        " GROUP BY %s having count(*) != 1;" % (
            m2o_field_old_model, table_old_model, m2o_field_old_model
        ))
    ko_ids = [x[0] for x in cr.fetchall()]
    for ko_id in ko_ids:
        query = (
            " SELECT %s"
            " FROM %s"
            " WHERE %s = %s;" % (
                field_old_model, table_old_model, m2o_field_old_model, ko_id))
        cr.execute(query)
        if binary_field:
            vals = [str(x[0][:]) for x in cr.fetchall()]
        else:
            vals = [x[0] for x in cr.fetchall()]
        value = func(cr, pool, ko_id, vals)
        if quick_request:
            query = (
                " UPDATE %s"
                " SET %s=%%s"
                " WHERE id = %%s" % (table_new_model, field_new_model))
            logged_query(
                cr, query, (value, ko_id))
        else:
            pool[registry_new_model].write(
                cr, SUPERUSER_ID, [ko_id],
                {field_new_model: value})


def convert_field_to_html(cr, table, field_name, html_field_name):
    """
    Convert field value to HTML value.
    """
    cr.execute(
        "SELECT id, %(field)s FROM %(table)s WHERE %(field)s IS NOT NULL" % {
            'field': field_name,
            'table': table,
        }
    )
    for row in cr.fetchall():
        logged_query(
            cr, "UPDATE %(table)s SET %(field)s = %s WHERE id = %s" % {
                'field': html_field_name,
                'table': table,
            }, (plaintext2html(row[1]), row[0])
        )
