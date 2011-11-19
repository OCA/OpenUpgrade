# -*- coding: utf-8 -*-

from osv import osv
import pooler
import logging
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

def rename_column(cr, table, columns):
    ### models are not yet initialized at pre time, of course
    #obj = pool.get(model)
    #if not obj:
    #    raise osv.except_osv("Migration: error renaming column, No such model: %s" % model, "")
    for old, new in columns:
        log.info("table %s, column %s: renaming to %s",
                 table, old, new)
        cr.execute('ALTER TABLE "%s" RENAME "%s" TO "%s"' % (table, old, new,))

def mgr_ir_model_fields(cr):
    cr.execute('ALTER TABLE ir_model_fields ADD COLUMN selectable BOOLEAN')
    cr.execute('UPDATE ir_model_fields SET selectable = FALSE')

def mgr_multi_company_default(cr, pool):
    #modules = pool.instanciate('base'), cr)
    from base.res import res_company
    obj = res_company.multi_company_default.createInstance(pool, 'base', cr)
    obj._auto_init(cr, {'module': 'base'})
    
def mgr_company_id(cr):
    # These tables add a new field for company_id.
    # The osv calls the _defaults function, which 
    # uses a model which is not instanciated at that point
    # (multi_company_default). We prevent this trigger from
    # happening by precreating the table, and fill them in 
    # the post script using the same _defaults function.
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
        pool = pooler.get_pool(cr.dbname)
        for table in renames.keys():
            rename_column(cr, table, renames[table])
        mgr_ir_model_fields(cr)
#        mgr_multi_company_default(cr, pool)
        mgr_company_id(cr)
        mgr_fix_test_results(cr)
    except Exception, e:
        osv.except_osv("Migration: error in pre-convert-fields.py: %s" % e, "")
        raise
