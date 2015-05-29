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
from openerp import pooler, SUPERUSER_ID

force_defaults = {
    'ir.mail_server': [('active', True)],
    'ir.model.access': [('active', True)],
    'res.company': [('custom_footer', True)],
    # We'll have to adapt the default for is_company in specific
    # modules. For instance, a migration script for hr
    # could reset is_company for partners associated with
    # employees
    'res.partner': [('is_company', True)],
}


def migrate_ir_translation(cr):
    openupgrade.logged_query(
        cr,
        """ UPDATE ir_translation
            SET state = 'translated'
            WHERE length(value) > 0;
        """)
    openupgrade.logged_query(
        cr,
        """ UPDATE ir_translation
            SET state = 'to_translate'
            WHERE state is NULL;
        """)


def migrate_company(cr):
    """
    Copy char value to new text column
    """
    cr.execute(
        """ UPDATE res_company
            SET rml_footer = rml_footer1
        """)


def migrate_base_contact(cr):
    """
    In v6.1, base_contact module has this structure:

    res.partner
    |
    |-> res.partner.address -|
    |-> res.partner.address -|
                             |-> res.partner.contact
    res.partner              |
    |                        |
    |-> res.partner.address -|

    And res.partner.contact contains information that is shared to linked
    res.partner.address via related fields.

    In v7, now that we remove res.partner.contact, we should copy
    res.partner.contact information on each linked address (that has been
    converted also to a res.partner record), but not create a new res.partner
    for each res.partner.contact.
    """
    cr.execute(
        "SELECT * FROM ir_module_module "
        "WHERE name = 'base_contact' and state = 'to remove';")
    if not cr.fetchall():
        return
    # Add non-existing columns that can be used with partner_lastname module
    cr.execute("ALTER TABLE res_partner "
               "ADD COLUMN firstname character varying;")
    cr.execute("ALTER TABLE res_partner "
               "ADD COLUMN lastname character varying;")
    # Update addresses with contact information
    openupgrade.logged_query(
        cr,
        """
        UPDATE res_partner
        SET lastname=contact.last_name,
            firstname=contact.first_name,
            mobile=contact.mobile,
            image=contact.photo,
            website=contact.website,
            lang=res_lang.code,
            active=contact.active,
            comment=contact.comment,
            country_id=contact.country_id,
            email=contact.email,
            birthdate=contact.birthdate
        FROM
            res_lang,
            res_partner_contact contact,
            res_partner_address
        WHERE
            res_lang.id = contact.lang_id AND
            res_partner.id =
            res_partner_address.openupgrade_7_migrated_to_partner_id AND
            contact.id = res_partner_address.contact_id
        """)


def migrate_partner_address(cr, pool):
    """ res.partner.address is obsolete. Move existing data to
    partner
    """
    partner_obj = pool.get('res.partner')
    cr.execute(
        "ALTER TABLE res_partner_address "
        "ADD column openupgrade_7_migrated_to_partner_id "
        " INTEGER")
    cr.execute(
        "ALTER TABLE res_partner_address ADD FOREIGN KEY "
        "(openupgrade_7_migrated_to_partner_id) "
        "REFERENCES res_partner ON DELETE SET NULL")
    fields = [
        'id', 'birthdate', 'city', 'country_id', 'email', 'fax', 'function',
        'mobile', 'phone', 'state_id', 'street', 'street2', 'type', 'zip',
        'partner_id', 'name', 'company_id'
        ]
    propagate_fields = [
        'lang', 'tz', 'customer', 'supplier',
    ]
    partner_found = []
    processed_ids = []

    # Make sure fields exist
    cr.execute(
        "SELECT column_name "
        "FROM information_schema.columns "
        "WHERE table_name = 'res_partner_address';")
    available_fields = set(i[0] for i in cr.fetchall())
    lost_fields = set(fields) - available_fields
    if lost_fields:
        openupgrade.logger.warning("""\
The following columns are not present in the table of %s: %s.

This can be the case if an additional module installed on your database changes
 the type of a regular column to a non-stored function or related field.
""", 'res_partner_address', ", ".join(lost_fields))
    fields = available_fields.intersection(fields)

    def set_address_partner(address_id, partner_id):
        cr.execute(
            "UPDATE res_partner_address "
            "SET openupgrade_7_migrated_to_partner_id = %s "
            "WHERE id = %s",
            (partner_id, address_id))

    def create_partner(address_id, vals, defaults):
        """
        Create a partner from an address. Update the vals
        with the defaults only if the keys do not occur
        already in vals. Register the created partner_id
        on the obsolete address table
        """
        for key in defaults:
            if key not in vals:
                vals[key] = defaults[key]

        partner_id = partner_obj.create(cr, SUPERUSER_ID, vals)
        set_address_partner(address_id, partner_id)

    def process_address_type(cr, whereclause, args=None):
        """
        Migrate addresses to partners, based on sql WHERE clause
        """
        openupgrade.logged_query(
            cr, "\n"
            "SELECT " + ', '.join(fields) + "\n"
            "FROM res_partner_address\n"
            "WHERE " + whereclause, args or ())
        for row in cr.fetchall():
            row_cleaned = [val or False for val in row]
            address = dict(zip(fields, row_cleaned))
            partner_vals = address.copy()
            partner_defaults = {
                # list of values that we should not overwrite
                # in existing partners
                'customer': False,
                'is_company': address['type'] != 'contact',
                'type': address['type'],
                'name': address['name'] or '/',
                }
            for f in ['name', 'id', 'type', 'partner_id']:
                del partner_vals[f]
            if not address['partner_id']:
                # Dangling addresses, create with not is_company,
                # not supplier and not customer
                create_partner(address['id'], partner_vals, partner_defaults)
            else:
                if address['partner_id'] not in partner_found:
                    # Main partner address
                    partner_obj.write(
                        cr, SUPERUSER_ID, address['partner_id'], partner_vals)
                    partner_found.append(address['partner_id'])
                    set_address_partner(address['id'], address['partner_id'])
                else:
                    # any following address for an existing partner
                    partner_vals.update({
                        'is_company': False,
                        'parent_id': address['partner_id']})
                    propagated_values = partner_obj.read(
                        cr, SUPERUSER_ID, address['partner_id'],
                        propagate_fields, load="_classic_write")
                    propagated_values.pop('id')
                    partner_vals.update(propagated_values)
                    create_partner(
                        address['id'], partner_vals, partner_defaults)
            processed_ids.append(address['id'])

    # Process all addresses, default type first
    process_address_type(cr, "type = 'default'")
    process_address_type(cr, "type IS NULL OR type = ''")
    process_address_type(cr, "id NOT IN %s", (tuple(processed_ids),))

    # Check that all addresses have been migrated
    cr.execute(
        "SELECT COUNT(*) FROM res_partner_address "
        "WHERE openupgrade_7_migrated_to_partner_id is NULL ")
    assert(not cr.fetchone()[0])


def update_users_partner(cr, pool):
    """
    Now that the fields exist on the model, finish
    the work of create_users_partner() in the pre script
    """
    partner_obj = pool.get('res.partner')
    cr.execute(
        # Can't use orm as these fields do not appear on the model
        # anymore
        "SELECT id, openupgrade_7_created_partner_id, context_lang, "
        "context_tz, " + openupgrade.get_legacy_name('user_email') + " "
        "FROM res_users "
        "WHERE openupgrade_7_created_partner_id IS NOT NULL")
    for row in cr.fetchall():
        partner_vals = {
            'user_ids': [(4, row[0])],
            'lang': row[2] or False,
            'tz': row[3] or False,
            'email': row[4] or False,
            }
        partner_obj.write(cr, SUPERUSER_ID, row[1], partner_vals)


def reset_currency_companies(cr, pool):
    """
    Having a company on currencies affects multicompany databases
    https://bugs.launchpad.net/openobject-server/+bug/1111298
    """
    currency_ids = pool.get('res.currency').search(
        cr, SUPERUSER_ID, [('company_id', '!=', False)],
        context={'active_test': False})
    pool.get('res.currency').write(
        cr, SUPERUSER_ID, currency_ids,
        {'company_id': False})


def migrate_res_company_logo(cr, pool):
    """
    Transfert logo from res_company to res_partner linked to the res_company,
    according to the new behaviour of V7:
    'res_company.logo' is now a field reladed to 'res_partner.image'
    """
    partner_obj = pool.get('res.partner')
    cr.execute("""
        SELECT partner_id, %s
        FROM res_company
        WHERE %s is not null""" % (
        openupgrade.get_legacy_name('logo'),
        openupgrade.get_legacy_name('logo')))
    for row in cr.fetchall():
        vals = {'image': row[1]}
        partner_obj.write(cr, SUPERUSER_ID, row[0], vals)


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    openupgrade.set_defaults(cr, pool, force_defaults, force=True)
    # circumvent orm when writing to record rules as the orm needs the
    # record rule's model to be instantiatable, which goes wrong at this
    # point for most models
    cr.execute('update ir_rule set active=True')
    migrate_ir_translation(cr)
    migrate_company(cr)
    migrate_partner_address(cr, pool)
    migrate_base_contact(cr)
    update_users_partner(cr, pool)
    reset_currency_companies(cr, pool)
    migrate_res_company_logo(cr, pool)
    openupgrade.load_xml(
        cr, 'base',
        'migrations/7.0.1.3/data.xml')
