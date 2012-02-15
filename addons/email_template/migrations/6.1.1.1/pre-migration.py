# -*- coding: utf-8 -*-

import os
from osv import osv
import logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = os.path.realpath( __file__ )

column_renames = {
    # this is a mapping per table from old column name
    # to new column name, e.g.
    #
    'email_template': [
        ('object_name', 'model_id'),
        # from_account?
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

def migrate(cr, version):
    try:
        logger.info("%s called", me)
        openupgrade.rename_columns(column_renames)
    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
