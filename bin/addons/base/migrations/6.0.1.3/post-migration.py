# -*- coding: utf-8 -*-

import pooler, logging
from openupgrade import openupgrade
logger = logging.getLogger('migrate')
MODULE="base"

obsolete_modules = [
    'account_report',
    'account_reporting',
    'account_tax_include',
    'board_account',
    'board_sale',
    'report_account', 
    'report_analytic',
    'report_analytic_line',
    'report_crm',
    'report_purchase',
    'report_sale',
    'pxgo_bank_statement_analytic',
]

def set_defaults_on_act_window(cr):
    """ The act window model has a constraint
    that checks the validity of the model on it.
    At migration time, this is inconvenient.
    Therefore, we set the defaults through SQL

    Replaces setting the following defaults
    #'ir.actions.act_window': [
    #    ('auto_search', True),
    #    ('context', '{}'),
    #    ('multi', False),
    #    ],    

    """
    cr.execute("""
        UPDATE ir_act_window
        SET auto_search = true,
            multi = false
        """)
    cr.execute("""
        UPDATE ir_act_window
        SET context = '{}'
        WHERE context is NULL
        """)
    cr.execute("""
        UPDATE ir_act_window
        SET context = '{}'
        WHERE context is NULL
        """)

defaults = {
    # False results in column value NULL
    # None value triggers a call to the model's default function 
    'ir.actions.todo': [
        ('restart', 'onskip'),
        ],
    'ir.attachment': [
        ('type', 'binary'),
        ('company_id', None),
        ],
    'ir.rule': [
        ('perm_create', True),
        ('perm_read', True),
        ('perm_unlink', True),
        ('perm_write', True),
        ],
    'res.company': [
        ('rml_header', ''),
        ('rml_header2', ''),
        ('rml_header3', ''),
        ],
    'res.currency': [
        ('company_id', None),
        ],
    'res.partner.address': [
        ('company_id', None),
        ],
    'res.partner': [
        ('company_id', None),
        ],
    'res.users': [
        ('company_id', None),
        ('company_ids', None),
        ('menu_tips', None),
        ],
    'ir.sequence': [
        ('company_id', None),
        ],
    }

def mgr_ir_rule(cr, pool):
    # rule_group migrated to groups, model_id, name
    # (and global, but that is a function)

    rule_obj = pool.get('ir.rule')
    rule_ids = rule_obj.search(cr, 1, [])
    rules = rule_obj.browse(cr, 1, rule_ids)
    
    for rule in rules:
        values = {}
        cr.execute("SELECT name, model_id FROM ir_rule_group WHERE id = %s", (rule.id,))
        row = cr.fetchone()
        if row:
            if row[0]:
                values['name'] = row[0]
            if row[1]:
                values['model_id'] = row[1]
        cr.execute(
            "SELECT group_rule_group_rel.group_id " +
            "FROM group_rule_group_rel, ir_rule " +
            "WHERE group_rule_group_rel.rule_group_id = ir_rule.rule_group " +
            "AND ir_rule.id = %s", (rule.id,)
            )
        groups = map(lambda x:x[0], cr.fetchall())
        if groups:
            values['groups'] = (6, 0, groups)
        rule_obj.write(cr, 1, [rule.id], values)
    # setting the constraint fails earlier at _auto_init
    cr.execute("ALTER TABLE ir_rule ALTER COLUMN model_id SET NOT NULL")

def get_or_create_title(cr, pool, name, domain):
    title_obj = pool.get('res.partner.title')
    title_ids = title_obj.search(
        cr, 1, [('name', '=', name), ('domain', '=', domain)]
        )
    if title_ids:
        return title_ids[0]
    return title_obj.create(
        cr, 1, {
            'name': name, 'shortcut': name, 'domain': domain,
            })

def mgr_res_partner_address(cr, pool):
    # In the pre script, we renamed the old function column, a many2one
    # to res.partner.function
    cr.execute(
        "UPDATE res_partner_address "
        "SET function = openupgrade_legacy_res_partner_function.name "
        "FROM openupgrade_legacy_res_partner_function "
        "WHERE openupgrade_legacy_res_partner_function.id "
        "= res_partner_address.tmp_mgr_function")
    cr.execute(
        "ALTER TABLE res_partner_address "
        "DROP COLUMN tmp_mgr_function CASCADE")
    # and the reverse: 'title' is now a many2one on res_partner_title
    cr.execute(
        "SELECT id, tmp_mgr_title FROM res_partner_address WHERE title IS NULL " +
        "AND tmp_mgr_title IS NOT NULL"
        )
    
    addr_obj = pool.get('res.partner.address')
    for row in cr.fetchall():
        title_id = get_or_create_title(cr, pool, row[1], 'contact')
        addr_obj.write(cr, 1, [row[0]], {'title': title_id})
    cr.execute("ALTER TABLE res_partner_address DROP COLUMN tmp_mgr_title CASCADE")

def mgr_res_partner(cr, pool):
    # ouch, duplicate code now for res_partner
    cr.execute(
        "SELECT id, tmp_mgr_title FROM res_partner WHERE title IS NULL " +
        "AND tmp_mgr_title IS NOT NULL"
        )
    
    partner_obj = pool.get('res.partner')
    for row in cr.fetchall():
        title_id = get_or_create_title(cr, pool, row[1], 'partner')
        partner_obj.write(cr, 1, [row[0]], {'title': title_id})
    cr.execute("ALTER TABLE res_partner DROP COLUMN tmp_mgr_title CASCADE")

def mgr_default_bank(cr, pool):
    # The 'bank' of a res.partner.bank (bank account) is now required.
    # Fill in the gap with a default, unknown bank.
    partner_bank_obj = pool.get('res.partner.bank')
    partner_bank_ids = partner_bank_obj.search(cr, 1, [('bank', '=', False)])
    if partner_bank_ids:
        bank_obj = pool.get('res.bank')
        bank_ids = bank_obj.search(cr, 1, [('code', '=', 'UNKNOW')])
        if bank_ids:
            bank_id = bank_ids[0]
        else:
            bank_id = bank_obj.create(cr, 1, dict(
                    code = 'UNKNOW',
                    name = 'Unknown Bank')),
        partner_bank_obj.write(cr, 1, partner_bank_ids, {'bank': bank_id})
            
def mgr_roles_to_groups(cr, pool):
    # Roles are replaced by groups.
    # Flatten the role hierarchy.
    # Migrate references in workflow.transition resources.
    cr.execute('ALTER TABLE res_roles ADD COLUMN mgr_group_id INTEGER')
    group_obj = pool.get('res.groups')
    cr.execute('SELECT id, name, parent_id FROM res_roles')
    rows = cr.fetchall()
    for row in rows:
        id, name, parent = row
        parents = [id]
        while parent:
            parents.append(parent)
            parent = None
            cr.execute('SELECT parent_id FROM res_roles where id = %s', (parent,))
            r = cr.fetchone()
            if r:
                parent = r[0]
        cr.execute(
            'SELECT DISTINCT uid FROM res_roles_users_rel WHERE rid in %s',
            (tuple(parents),)
            )
        user_ids = [r[0] for r in cr.fetchall()]
        group_id = group_obj.create(
            cr, 1, {'name': name + ' (migrated role)', 'users': [(6, 0, user_ids)],}
            )
        cr.execute(
            'UPDATE res_roles SET mgr_group_id = %s WHERE id = %s',
            (group_id, id,)
            )
        # TODO maybe it is better to converse migrated roles with the groups
        # that are associated with the transition in V6 instead of adapting
        # the group_id to the group that contains the users from the old role.
        cr.execute(
            'UPDATE wkf_transition SET group_id = res_roles.mgr_group_id ' +
            'FROM res_roles WHERE wkf_transition.tmp_mgr_role_id = res_roles.id'
            )
    # Do not remove the roles model or the added group field,
    # to use in other modules.
    #   cr.execute("ALTER res_roles DROP COLUMN mgr_group_id")
    # But do remove the role column of the workflow transitions
    cr.execute("ALTER TABLE wkf_transition DROP COLUMN tmp_mgr_role_id")

def mgr_res_currency(cr, pool):
    # migrate code field to name
    cr.execute("UPDATE res_currency SET name = code WHERE code IS NOT NULL")
    cr.execute("ALTER TABLE res_currency DROP COLUMN code")

def mgr_ir_module_module(cr):
    # deal with changed module names in order to prevent
    # 'certificate not unique' error
    cr.execute("UPDATE ir_module_module SET name = 'project_planning' WHERE certificate = '0034901836973'")
    cr.execute("UPDATE ir_module_module SET name = 'association' WHERE certificate = '0078696047261'")

def mgr_res_users(cr):
    # you cannot have a menu action as home action anymore
    # this causes an infinite loop in the web client
    cr.execute(
        "UPDATE res_users SET action_id = NULL " +
        "FROM ir_actions WHERE action_id = ir_actions.id " +
        "AND ir_actions.usage = 'menu'"
        )

def mark_obsolete_modules(cr):
    """
    Remove modules that are known to be obsolete
    in this version of the OpenERP server.
    """
    openupgrade.logged_query(
        cr, """
        UPDATE
            ir_module_module
        SET 
            state='to remove'
        WHERE
            state='installed'
            AND name in %s
        """,
        (tuple(obsolete_modules),))

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    set_defaults_on_act_window(cr)
    openupgrade.set_defaults(cr, pool, defaults)
    mgr_ir_rule(cr, pool)
    mgr_res_partner_address(cr, pool)
    mgr_res_partner(cr, pool)
    mgr_default_bank(cr, pool)
    mgr_roles_to_groups(cr, pool)
    mgr_res_currency(cr, pool)
    mgr_ir_module_module(cr)
    mgr_res_users(cr)
    mark_obsolete_modules(cr)

