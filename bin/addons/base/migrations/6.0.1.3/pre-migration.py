# -*- coding: utf-8 -*-

from osv import osv
import pooler
import logging
from openupgrade import openupgrade
log = logging.getLogger('migrate')

renames = {
    # this is a mapping per table from old column name
    # to new column name
    'ir_property': [
        ('value', 'value_reference'),
        ],
    'res_partner_address': [
        ('function', 'tmp_mgr_function'),
        ('title', 'tmp_mgr_title'),
        ],
    'res_partner': [
        ('title', 'tmp_mgr_title'),
        ],
    'wkf_transition': [
        ('role_id', 'tmp_mgr_role_id'),
        ],
    }

def mgr_ir_model_fields(cr):
    cr.execute('ALTER TABLE ir_model_fields ADD COLUMN selectable BOOLEAN')
    cr.execute('UPDATE ir_model_fields SET selectable = FALSE')

def mgr_company_id(cr):
    # These models add a new field for company_id, to be filled
    # by the post.py script
    # Otherwise, the osv would create it and call the _defaults function,
    # using a model that is not instanciated at that point
    # (multi_company_default).
    for table in (
        'ir_attachment', 'res_currency', 
        'res_partner_address', 'res_partner',
        'ir_sequence',
        ):
        # passing table name as a cursor param is not supported,
        # using direct python substitution
        cr.execute('ALTER TABLE "%s" ADD COLUMN company_id INTEGER' % table)

def mgr_fix_test_results(cr):
    cr.execute("UPDATE res_currency_rate SET rate = 59.9739 " +
               "FROM ir_model_data " + 
               "WHERE ir_model_data.res_id = res_currency_rate.id " +
               "AND ir_model_data.module = 'base' " +
               "AND ir_model_data.model = 'res.currency.rate' " +
               "AND ir_model_data.name = 'rateINR'")
    if not cr.rowcount:
        import pdb
        pdb.set_trace()
        raise osv.except_osv("Migration: error setting INR rate in demo data, no row found", "")

def migrate(cr, version):
    try:
        # this method called in a try block too
        log.info("base:pre.py now called")
        pool = pooler.get_pool(cr.dbname)
        openupgrade.rename_columns(cr, renames)
        mgr_ir_model_fields(cr)
        mgr_company_id(cr)
        mgr_fix_test_results(cr)
    except Exception, e:
        log.info("Migration: error in pre-convert-fields.py: %s", e)
        osv.except_osv("Migration: error in pre-convert-fields.py: %s" % e, "")
        raise
