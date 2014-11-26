# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

from openerp import pooler, SUPERUSER_ID
from openupgrade import openupgrade
from openupgrade.openupgrade_70 import set_partner_id_from_partner_address_id as fix_partner

def migrate_partners(cr, pool):
    fix_partner(cr, pool, 'crm.meeting', 'partner_id',
                openupgrade.get_legacy_name('partner_address_id'))
    fix_partner(cr, pool, 'crm.lead', 'partner_id',
                openupgrade.get_legacy_name('partner_address_id'))
    fix_partner(cr, pool, 'crm.phonecall', 'partner_id',
                openupgrade.get_legacy_name('partner_address_id'))

def create_section_mail_aliases(cr, pool, uid=SUPERUSER_ID):
    """
    Create mail aliases for each existing crm.case.section
    """
    # Pools
    crm_case_section = pool.get('crm.case.section')
    mail_alias = pool.get('mail.alias')
    # Get case_sections
    openupgrade.logged_query(cr, """SELECT id, name from crm_case_section;""")
    vals = cr.fetchall()
    # Create alias for each section
    for id, name in vals:
        fields = {
            'alias_name': name,
            'alias_defaults': {'section_id': id, 'type': 'lead'},
        }
        alias_id = mail_alias.create_unique_alias(cr, uid, fields,
                                                  model_name="crm.lead")
        crm_case_section.write(cr, uid, [id], {'alias_id': alias_id})

@openupgrade.migrate()
def migrate(cr, version):
    """
    * Create mail aliases for crm case section,
    * Load xml data (Mail alias and updates to CRM stages)
    * Change categ_id to many to many
    """
    pool = pooler.get_pool(cr.dbname)
    openupgrade.load_xml(
        cr, 'crm',
        'migrations/7.0.1.0/data.xml')
    create_section_mail_aliases(cr, pool)
    # Migrate m2o categ_id to m2m categ_ids
    openupgrade.m2o_to_m2m(cr, pool.get('crm.lead'), 'crm_lead', 'categ_ids',
                           openupgrade.get_legacy_name('categ_id'))
    migrate_partners(cr, pool)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
