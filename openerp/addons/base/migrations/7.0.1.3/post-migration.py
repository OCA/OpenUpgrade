# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2012-2013 Therp BV (<http://therp.nl>)
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

from openupgrade import openupgrade
from openerp import SUPERUSER_ID

force_defaults = {
    'ir.model.access': [('active', True)],
    'ir.rule': [('active', True)],
    'res.company': [('custom_footer', True)],
    # We'll have to adapt the default for is_company in specific
    # modules. For instance, a migration script for hr
    # could reset is_company for partners associated with
    # employees
    'res.partner': [('is_company', True)],
}

def migrate_company(cr):
    """
    Copy char value to new text column
    """
    cr.execute(
        """ UPDATE res_company
            SET rml_footer = rml_footer1
        """)

def migrate_partner_address(cr, pool):
    """ res.partner.address is obsolete. Move existing data to
    partner

    TODO: break hard when base_contact is installed
    """
    partner_obj = self.pool.get('res.partner')
    cr.execute(
        "ALTER TABLE res_partner_address "
        "ADD column openupgrade_7_migrated_to_partner_id "
        " INTEGER")
    cr.execute(
        "ALTER TABLE 'res_partner_address' ADD FOREIGN KEY "
        "'openupgrade_7_migrated_to_partner_id' "
        "REFERENCES 'res_partner' ON DELETE SET NULL")
    fields = [
        'id', 'birthdate', 'city', 'country_id', 'email', 'fax', 'function',
        'mobile', 'phone', 'state_id', 'street', 'street2', 'type', 'zip',
        'partner_id', 'name',
        ]
    partner_found = []
    processed_ids = []

    def create_partner(address_id, vals, defaults):
        """
        Create a partner from an address. Update the vals
        with the defaults only if the keys do not occur
        already in vals. Register the created partner_id
        on the obsolete address table
        """
        for key, value in defaults:
            if key not in vals:
                vals[key] = value

        partner_id = partner_obj.create(cr, SUPERUSER_ID, vals)
        cr.execute(
            "UPDATE res_partner_addres "
            "SET openupgrade_7_migrated_to_partner_id = %s "
            "WHERE id = %s",
            (partner_id, address_id))

    def process_address_type(cr, typeclause, args=None):
        """
        Migrate addresses to partners, based on sql type clause
        """
        cr.execute(
            "SELECT " + ', '.join(fields) + " FROM res_partner_address "
            "WHERE type " + typeclause, args or ()
            )
        for row in cr.fetchall():
            row_cleaned = [val or False for val in row]
            address = dict(zip(fields, row_cleaned))
            partner_vals = address.copy()
            partner_defaults = {
                # list of values that we should not overwrite
                # in existing partners
                'customer': False,
                'is_company': partner_vals['type'] != 'contact'
                }
            del partner_vals['id']
            del partner_vals['partner_id']
            if not address['partner_id']:
                # Dangling addresses, create with not is_company,
                # not supplier and not customer
                partner_vals['name'] = partner_vals['name'] or '/'
                create_partner(address['id'], partner_vals, partner_defaults)
            else:
                if address['partner_id'] not in partner_found:
                    # Main partner address
                    partner_obj.write(
                        cr, SUPERUSER_ID, address['partner_id'], partner_vals)
                    partner_found.append(address['partner_id'])
                else:
                    # any following address for an existing partner
                    partner_vals.update({
                            'name': partner_vals['name'] or '/',
                            'is_company': False,
                            'parent_id': address['partner_id']})
                    create_partner(
                        address['id'], partner_vals, partner_defaults)
            processed_ids.append(address['id'])

    # Process all addresses, default type first 
    process_address_type(cr, "= 'default'")
    process_address_type(cr, "IS NULL")
    process_address_type(cr, "= ''")
    process_address_type(cr, "NOT IN %s", (tuple(processed_ids),))

def create_users_partner(cr, pool):
    """ Users now have an inherits on res.partner """
    partner_obj = self.pool.get('res.partner')
    cr.execute(
        # Can't use orm as these fields to not appear on the model
        # anymore
        "SELECT name, context_lang, context_tz, user_email, active "
        "FROM res_users WHERE partner_id IS NULL")
    for row in cr.fetchall():
        user_id = row.pop(0)
        partner_vals = dict(
            zip(['name', 'lang', 'tz', 'email', 'active'], row))
        partner_vals.update({
                'user_ids': [(4, user_id)],
                'customer': False,
                })
        partner_obj.create(cr, SUPERUSER_ID, partner_vals)

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    openupgrade_set_defaults(cr, pool, force_defaults, force=True)
    migrate_company(cr)
    migrate_partner_address(cr, pool)
    create_users_partner(cr, pool)
