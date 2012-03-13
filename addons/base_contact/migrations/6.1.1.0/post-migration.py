# -*- coding: utf-8 -*-

from osv import osv
import logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = __file__


def _migrate_jobs(cr):
    if not openupgrade.table_exists(cr, 'res_partner_job'):
        return
    openupgrade.logged_query(cr,"""
        ALTER TABLE res_partner_address ADD COLUMN x_openupgrade_job_id integer
    """)
    openupgrade.logged_query(cr,"""
        INSERT INTO
            res_partner_address
            (create_uid,create_date,write_date,write_uid,location_id,contact_id,
             function,phone,fax,email,active,partner_id,company_id,
             x_openupgrade_job_id)
        SELECT
            job.create_uid,job.create_date,job.write_date,job.write_uid,job.address_id,job.contact_id,
            job.function,job.phone,job.fax,job.email,true,adr.partner_id,adr.company_id,
            job.id
        FROM
            res_partner_job job
        join
            res_partner_address adr on address_id=adr.id
    """)

def migrate(cr, version):
    if not version:
        return
    try:
        logger.info("%s called", me)
        _migrate_jobs(cr)
    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))

