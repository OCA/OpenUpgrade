# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2011-2012 Therp BV (<http://therp.nl>)
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
import traceback
import release
from osv import osv
import pooler
import tools
import openupgrade_tools

logger = logging.getLogger('OpenUpgrade')

__all__ = [
    'migrate',
    'load_data',
    'rename_columns',
    'rename_tables',
    'drop_columns',
    'table_exists',
    'column_exists',
    'logged_query',
    'delete_model_workflow',
    'set_defaults',
    'update_module_names',
    'add_ir_model_fields',
    'rename_models',
    'rename_xmlids',
    'get_legacy_name',
]    

def load_data(cr, module_name, filename, idref=None, mode='init'):
    """
    Load an xml or csv data file from your post script. The usual case for this is the
    occurrence of newly added essential or useful data in the module that is
    marked with "noupdate='1'" and without "forcecreate='1'" so that it will
    not be loaded by the usual upgrade mechanism. Leaving the 'mode' argument to
    its default 'init' will load the data from your migration script.
    
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
    :param mode: one of 'init', 'update', 'demo'. Always use 'init' for adding new items \
    from files that are marked with 'noupdate'. Defaults to 'init'.

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
            tools.convert_csv_import(cr, module_name, pathname, fp.read(), idref, mode, noupdate)
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

    :param column_spec: a hash with table keys, with lists of tuples as values. \
    Tuples consist of (old_name, new_name).

    """
    for table in column_spec.keys():
        for (old, new) in column_spec[table]:
            logger.info("table %s, column %s: renaming to %s",
                     table, old, new)
            cr.execute('ALTER TABLE "%s" RENAME "%s" TO "%s"' % (table, old, new,))
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
        cr.execute('UPDATE ir_model_fields SET relation = %s '
                   'WHERE relation = %s', (new, old,))
        cr.execute('UPDATE ir_model_data SET model = %s '
                   'WHERE model = %s', (new, old,))
        #TODO: update foreign keys using
        #http://stackoverflow.com/questions/1152260/postgres-sql-to-list-table-foreign-keys

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

def set_defaults(cr, pool, default_spec, force=False):
    """
    Set default value. Useful for fields that are newly required. Uses orm, so
    call from the post script.
    
    :param default_spec: a hash with model names as keys. Values are lists of \
    tuples (field, value). None as a value has a special meaning: it assigns \
    the default value. If this value is provided by a function, the function is \
    called as the user that created the resource.
    :param force: overwrite existing values. To be used for assigning a non- \
    default value (presumably in the case of a new column). The ORM assigns \
    the default value as declared in the model in an earlier stage of the \
    process. Beware of issues with resources loaded from new data that \
    actually do require the model's default, in combination with the post \
    script possible being run multiple times.
    """

    def write_value(ids, field, value):
        logger.debug("model %s, field %s: setting default value of resources %s to %s",
                 model, field, ids, unicode(value))
        obj.write(cr, 1, ids, {field: value})

    for model in default_spec.keys():
        obj = pool.get(model)
        if not obj:
            raise osv.except_osv("Migration: error setting default, no such model: %s" % model, "")

        for field, value in default_spec[model]:
            domain = not force and [(field, '=', False)] or []
            ids = obj.search(cr, 1, domain)
            if not ids:
                continue
            if value is None:
                # Set the value by calling the _defaults of the object.
                # Typically used for company_id on various models, and in that
                # case the result depends on the user associated with the object.
                # We retrieve create_uid for this purpose and need to call the _defaults
                # function per resource. Otherwise, write all resources at once.
                if field in obj._defaults:
                    if not callable(obj._defaults[field]):
                        write_value(ids, field, obj._defaults[field])
                    else:
                        # existence users is covered by foreign keys, so this is not needed
                        # cr.execute("SELECT %s.id, res_users.id FROM %s LEFT OUTER JOIN res_users ON (%s.create_uid = res_users.id) WHERE %s.id IN %s" %
                        #                     (obj._table, obj._table, obj._table, obj._table, tuple(ids),))
                        cr.execute("SELECT id, COALESCE(create_uid, 1) FROM %s " % obj._table + "WHERE id in %s", (tuple(ids),))
                        # Execute the function once per user_id
                        user_id_map = {}
                        for row in cr.fetchall():
                            user_id_map.setdefault(row[1], []).append(row[0])
                        for user_id in user_id_map:
                            write_value(
                                user_id_map[user_id], field,
                                obj._defaults[field](obj, cr, user_id, None))
                else:
                    error = ("OpenUpgrade: error setting default, field %s with "
                             "None default value not in %s' _defaults" % (
                            field, model))
                    logger.error(error)
                    # this exeption seems to get lost in a higher up try block
                    osv.except_osv("OpenUpgrade", error)
            else:
                write_value(ids, field, value)
    
def logged_query(cr, query, args=None):
    if args is None:
        args = []
    res = cr.execute(query, args)
    logger.debug('Running %s', query)
    if not res:
        query = query % args
        logger.warn('No rows affected for query "%s"', query)
    return res

def column_exists(cr, table, column):
    """ Check whether a certain column exists """
    cr.execute(
        'SELECT count(attname) FROM pg_attribute '
        'WHERE attrelid = '
        '( SELECT oid FROM pg_class WHERE relname = %s ) '
        'AND attname = %s',
        (table, column));
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
    return 'openupgrade_legacy_%s_%s' % (
        release.major_version.replace('.', '_'),
        original_name)
        
def add_module_dependencies(cr, module_list):
    """
    Select (new) dependencies from the modules in the list
    so that we can inject them into the graph at upgrade
    time. Used in the modified OpenUpgrade Server,
    not to be used in migration scripts
    """
    dependencies = module_list
    while dependencies:
        cr.execute("""
            SELECT DISTINCT dep.name
            FROM
                ir_module_module,
                ir_module_module_dependency dep
            WHERE
                module_id = ir_module_module.id
                AND ir_module_module.name in %s
                AND dep.name not in %s
            """, (tuple(dependencies), tuple(module_list),))
        dependencies = [x[0] for x in cr.fetchall()]
        module_list += dependencies
    return module_list

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
            stage =  'unknown'
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
                    (module, filename, e))
                logger.error(traceback.format_exc())
                raise
        return wrapped_function
    return wrap
