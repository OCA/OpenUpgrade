# -*- coding: utf-8 -*-
from osv import osv
import pooler, logging
from openerp import SUPERUSER_ID
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = __file__

def write_account_report_type(cr):
    pool = pooler.get_pool(cr.dbname)
    type_obj = pool.get('account.account.type')
    cr.execute(
        "SELECT id, report_type_tmp FROM account_account_type "
        "WHERE report_type_tmp IS NOT NULL")
    for row in cr.fetchall():
        type_obj.write(
            cr, SUPERUSER_ID, row[0], {'report_type': row[1]})
    openupgrade.drop_columns(
        cr, [('account_account_type', 'report_type_tmp')])

def migrate(cr, version):
    try:
        logger.info("%s called", me)
        openupgrade.load_data(cr, 'account', 'migrations/6.1.1.1/data/data_account_type.xml')
        openupgrade.load_data(cr, 'account', 'migrations/6.1.1.1/data/account_financial_report_data.xml')
        openupgrade.load_data(cr, 'account', 'migrations/6.1.1.1/data/invoice_action_data.xml')
        write_account_report_type(cr)

    except Exception, e:
        raise osv.except_osv("BREAK", "OpenUpgrade", '%s: %s' % (me, e))
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
