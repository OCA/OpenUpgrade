# -*- coding: utf-8 -*-
from osv import osv
import pooler
import logging
import tools
from os.path import join as opj

__all__ = ['load_xml', 'rename_columns', 'set_defaults']

logger = logging.getLogger('migrate')

def load_xml(cr, m, filename, idref=None, mode='init'):
    """
    Load an xml data file from your post script.
    
    Theoretically, you could simply load a stock file from the module, but be 
    careful not to reinitialize any data that could have been customized.
    Preferably, select only the newly added items. Copy these to a file
    in your migrations directory and load that file.
    Leave it to the user to actually delete existing resources that are
    marked with 'noupdate' (other named items will be deleted
    automatically).


    :param m: the name of the module
    :param filename: the path to the filename, relative to the module \
    directory.
    :param idref: optional hash with ?id mapping cache?
    :param mode: one of 'init', 'update', 'demo'. Always use 'init' for adding new items \
    from files that are marked with 'noupdate'. Defaults to 'init'.

    """

    if idref is None:
        idref = {}
    logger.info('%s: loading %s' % (m, filename))
    fp = tools.file_open(opj(m, filename))
    try:
        tools.convert_xml_import(cr, m, fp, idref, mode=mode)
    finally:
        fp.close()

def rename_columns(cr, column_spec):
    """
    Rename table columns. Typically called in the pre script.

    :param column_spec: a hash with table keys, with lists of tuples as values. \
    Tuples consist of (old_name, new_name).

    """
    for table in column_spec.keys():
        for old, new in column_spec[table]:
            logger.info("table %s, column %s: renaming to %s",
                     table, old, new)
            cr.execute('ALTER TABLE "%s" RENAME "%s" TO "%s"' % (table, old, new,))

def set_defaults(cr, pool, default_spec):
    """
    Set default value. Useful for fields that are newly required. Uses orm, so
    call from the post script.
    
    :param default_spec: a hash with model names as keys. Values are lists of \
    tuples (field, value). None as a value has a special meaning: it assigns \
    the default value. If this value is provided by a function, the function is \
    called as the user that created the resource.
    """

    def write_value(ids, field, value):
        logger.info("model %s, field %s: setting default value of %d resources to %s",
                 model, field, len(ids), unicode(value))
        obj.write(cr, 1, ids, {field: value})

    for model in default_spec.keys():
        obj = pool.get(model)
        if not obj:
            raise osv.except_osv("Migration: error setting default, no such model: %s" % model, "")

    for field, value in default_spec[model]:
        ids = obj.search(cr, 1, [(field, '=', False)])
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
                    fetchdict = dict(cr.fetchall())
                    for id in ids:
                        write_value([id], field, obj._defaults[field](obj, cr, fetchdict.get(id, 1), None))
                        if id not in fetchdict:
                            logger.info("model %s, field %s, id %d: no create_uid defined or user does not exist anymore",
                                     (model, field, id))
            else:
                logger.error("OpenUpgrade: error setting default, field %s with " +
                          "None default value not in %s' _defaults",
                          (field, model))
                # this exeption seems to get lost in a higher up try block
                osv.except_osv("Migration: error setting default, field " +
                               "%s with None default value not in %s' _defaults" %
                               (field, model), "")
        else:
            write_value(ids, field, value)
