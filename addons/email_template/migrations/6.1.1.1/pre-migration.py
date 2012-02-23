# -*- coding: utf-8 -*-

import os
from osv import osv
import logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = __file__

column_renames = {
    # this is a mapping per table from old column name
    # to new column name
    #
    'email_template': [
        ('object_name', 'model_id'),
        ('def_to', 'email_to'),
        ('def_cc', 'email_cc'),
        ('def_bcc', 'email_bcc'),
        ('def_subject', 'subject'),
        ('def_body_text', 'body_text'),
        ('def_body_html', 'body_html'),
        ('use_sign', 'user_signature'),
        ('file_name', 'report_name'),
        ],
    }

def fix_email_from(cr):
    """ 
    Prematurely add the email_from column and fill it with the
    address from the obsolete account model.
    """
    openupgrade.logged_query(
        cr,
        "ALTER TABLE email_template ADD COLUMN email_from "
        "CHARACTER VARYING (128)")
    openupgrade.logged_query(
        cr,
        "UPDATE email_template SET email_from = email_id "
        "FROM email_template_account WHERE "
        "email_template.from_account = email_template_account.id")

def migrate(cr, version):
    if not version:
        return
    try:
        logger.info("%s called", me)
        if not openupgrade.column_exists(cr, 'email_template', 'user_signature'):
            openupgrade.rename_columns(cr, column_renames)
            fix_email_from(cr)
            openupgrade.delete_model_workflow(cr, 'email_template.account')
    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
