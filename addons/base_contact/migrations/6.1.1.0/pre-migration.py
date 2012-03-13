# -*- coding: utf-8 -*-

from osv import osv
import logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = __file__


def _migrate_last_name(cr):
    column_renames = {
        'res_partner_contact': [
            ('name', 'last_name'),
            ],
        }
    #if openupgrade.table_exists(cr, 'res_partner_contact'):
    #    return
    #if not openupgrade.column_exists(cr, 'res_partner_contact', 'last_name'):
    #    return
    openupgrade.rename_columns(cr, column_renames)

def _migrate_birthdate(cr):
    openupgrade.logged_query(cr, 'alter table res_partner_contact alter column birthdate type character varying(64);')

def migrate(cr, version):
    if not version:
        return
    try:
        logger.info("%s called", me)
        _migrate_last_name(cr)
        _migrate_birthdate(cr)
    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
