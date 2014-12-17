# -*- coding: utf-8 -*-
from openupgrade_tools import table_exists


def log_xml_id(cr, module, xml_id):
    """
    Log xml_ids at load time in the records table.
    Called from openerp/tools/convert.py:xml_import._test_xml_id()

    # Catcha's
    - The module needs to be loaded with 'init', or the calling method
    won't be called. This can be brought about by installing the
    module or updating the 'state' field of the module to 'to install'
    or call the server with '--init <module>' and the database argument.

    - Do you get the right results immediately when installing the module?
    No, sorry. This method retrieves the model from the ir_model_table, but
    when the xml id is encountered for the first time, this method is called
    before the item is present in this table. Therefore, you will not
    get any meaningful results until the *second* time that you 'init'
    the module.

    - The good news is that the openupgrade_records module that comes
    with this distribution allows you to deal with all of this with
    one click on the menu item Settings -> Customizations ->
    Database Structure -> OpenUpgrade -> Generate Records

    - You cannot reinitialize the modules in your production database
    and expect to keep working on it happily ever after. Do not perform
    this routine on your production database.

    :param module: The module that contains the xml_id
    :param xml_id: the xml_id, with or without 'module.' prefix
    """
    if not table_exists(cr, 'openupgrade_record'):
        return
    if not '.' in xml_id:
        xml_id = '%s.%s' % (module, xml_id)
    cr.execute(
        "SELECT model FROM ir_model_data "
        "WHERE module = %s AND name = %s",
        xml_id.split('.'))
    record = cr.fetchone()
    if not record:
        print "Cannot find xml_id %s" % xml_id
        return
    else:
        cr.execute(
            "SELECT id FROM openupgrade_record "
            "WHERE module=%s AND model=%s AND name=%s AND type=%s",
            (module, record[0], xml_id, 'xmlid'))
        if not cr.fetchone():
            cr.execute(
                "INSERT INTO openupgrade_record "
                "(module, model, name, type) values(%s, %s, %s, %s)",
                (module, record[0], xml_id, 'xmlid'))
