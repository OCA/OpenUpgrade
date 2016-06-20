# -*- coding: utf-8 -*-
# © 2016 Sylvain LE GAL <https://twitter.com/legalsylvain>
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_renames = {
    'account_bank_statement': [
        ('closing_date', 'date_done'),
    ],
    'account_account_type': [
        ('close_method', None),
    ],
    'account_bank_statement_line': [
        ('journal_entry_id', None),
    ],
}

column_copies = {
    'account_bank_statement': [
        ('state', None, None),
    ],
    'account_journal': [
        ('type', None, None),
    ],
    'account_tax': [
        ('type_tax_use', None, None),
    ],
    'account_tax_template': [
        ('type_tax_use', None, None),
    ],
}

table_renames = [
    ('account_statement_operation_template', 'account_operation_template'),
    ('account_tax_code', 'account_tax_group')]


def account_account_type(cr):

    #Drop Not Nulls
    cr.execute("""
    ALTER TABLE account_account_type ALTER COLUMN close_method DROP NOT NULL
    """)
    cr.execute("""
    ALTER TABLE account_account_type ALTER COLUMN code DROP NOT NULL
    """)
    cr.execute("""
    ALTER TABLE account_account_type ALTER COLUMN report_type DROP NOT NULL
    """)

    # Drop Constraint to delete accounts having type view.
    cr.execute("""
    ALTER TABLE account_account DROP CONSTRAINT account_account_parent_id_fkey
    """)
    cr.execute("""
    DELETE FROM account_account WHERE type = 'view'
    """)

    # Add Column 'type' to later insert values into it.
    cr.execute("""
    ALTER TABLE account_account_type ADD type VARCHAR
    """)

    # Retrieve distinct account_type with the combination of internal type 
    cr.execute("""
    SELECT DISTINCT(user_type), type FROM account_account ORDER BY user_type
    """)

    account_types = cr.dictfetchall()

    for x in account_types:
        internal_type = str(x['type'])
        user_type = int(x['user_type'])

        # Retrieve accounts with specified type
        cr.execute("""
        SELECT id, user_type, type FROM account_account
        WHERE user_type = %(user_type_id)s AND type = '%(internal_type)s'
        """ % {'internal_type': internal_type, 'user_type_id' : user_type})

        accounts = cr.dictfetchall()

        # Create the combination of account type name and its type
        cr.execute("""
        SELECT name FROM account_account_type WHERE id = %(user_type_id)s
        """ % {'user_type_id': user_type})

        account_type_name = cr.fetchone()
        combination = str(account_type_name[0]) + ' - ' + internal_type

        cr.execute("""
        INSERT INTO account_account_type (name, type)
        VALUES ('%(combination)s','%(type)s') RETURNING id
        """ % {'combination': combination, 'type': internal_type})

        account_type = cr.fetchone()
        account_type_id = int(account_type[0])

        # Update the accounts with new account type combination
        for a in accounts:
            account_id = int(a['id'])
            cr.execute("""
            UPDATE account_account SET user_type = %(type)s WHERE id = %(id)s
            """ % {'id': account_id, 'type': account_type_id})

PROPERTY_FIELDS = {
    ('product.category', 'property_account_expense_categ',
     'property_account_expense_categ_id'),
    ('product.category', 'property_account_income_categ',
     'property_account_income_categ_id'),
    ('res.partner', 'property_account_payable', 'property_account_payable_id'),
    ('res.partner', 'property_account_receivable',
     'property_account_receivable_id'),
}


def migrate_properties(cr):
    for model, name_v8, name_v9 in PROPERTY_FIELDS:
        openupgrade.logged_query(cr, """
            update ir_model_fields
            set name = '{name_v9}'
            where name = '{name_v8}'
            and model = '{model}'
            """.format(model=model, name_v8=name_v8, name_v9=name_v9))
        openupgrade.logged_query(cr, """
            update ir_property
            set name = '{name_v9}'
            where name = '{name_v8}'
            """.format(name_v8=name_v8, name_v9=name_v9))


@openupgrade.migrate()
def migrate(cr, version):
    account_account_type(cr)
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.copy_columns(cr, column_copies)
    migrate_properties(cr)
