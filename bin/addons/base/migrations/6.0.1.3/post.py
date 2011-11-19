# -*- coding: utf-8 -*-

from osv import osv
import pooler, logging
log = logging.getLogger('migrate')

defaults = {
    # False results in column value NULL
    # None value triggers a call to the model's default function 
    'ir.actions.act_window': [
        ('auto_search', True),
        ('context', '{}'),
        ('multi', False),
        ],    
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

def set_default(cr, pool, model, fields):
    obj = pool.get(model)
    if not obj:
        raise osv.except_osv("Migration: error setting default, no such model: %s" % model, "")

    def write_value(ids, field, value):
        log.info("model %s, field %s: setting default value of %d resources to %s",
                 model, field, len(ids), unicode(value))
        obj.write(cr, 1, ids, {field: value})

    for field, value in fields:
        ids = obj.search(cr, 1, [(field, '=', False)])
        if not ids:
            continue
        if value is None:
            # Set the value by calling the _defaults of the object.
            # Typically used for company_id on various models, and in that
            # case the result depends on the user associated with the object.
            # We retrieve create_uid for this purpose and need to call the _defaults
            # function per resource. Otherwise, write all resources at once.
            if field in obj._defaults:
                if not callable(obj._defaults[field]):
                    write_value(ids, field, obj._defaults[field])
                else:
                    # existence users is covered by foreign keys
#                    cr.execute("SELECT %s.id, res_users.id FROM %s LEFT OUTER JOIN res_users ON (%s.create_uid = res_users.id) WHERE %s.id IN %s" %
#                               (obj._table, obj._table, obj._table, obj._table, tuple(ids),))
                    cr.execute("SELECT id, COALESCE(create_uid, 1) FROM %s WHERE id in %s" % (obj._table, tuple(ids),))
                    fetchdict = dict(cr.fetchall())
                    for id in ids:
                        write_value([id], field, obj._defaults[field](obj, cr, fetchdict.get(id, 1), None))
                        if id not in fetchdict:
                            log.info("model %s, field %s, id %d: no create_uid defined or user does not exist anymore",
                                     (model, field, id))
            else:
                osv.except_osv("Migration: error setting default, field %s with None default value not in %s' _defaults" % (field, model), "")
        else:
            write_value(ids, field, value)

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
        "UPDATE res_partner_address SET function = res_partner_function.name " +
        "FROM res_partner_function " +
        "WHERE res_partner_function.id = res_partner_address.tmp_mgr_function"
        )
    cr.execute("ALTER TABLE res_partner_address DROP COLUMN tmp_mgr_function CASCADE")
    cr.execute("DROP TABLE res_partner_function")

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
            bank_id = bank_obj.create(cursor, uid, dict(
                    code = info.code or 'UNKNOW',
                    name = info.name or _('Unknown Bank'),
                    ))
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
    # deal with changed module names
    cr.execute("UPDATE ir_module_module SET name = 'project_planning' WHERE certificate = '0034901836973'")
    cr.execute("UPDATE ir_module_module SET name = 'association' WHERE certificate = '0078696047261'")

def mgr_clean_act_window(cr, pool):
    # remove invalid act_windows which refer non existing models
    obj = pool.get('ir.actions.act_window')
    acts = obj.browse(cr, 1, obj.search(cr, 1, []))
    to_unlink = []
    for action in acts:
        if (not pool.get(action.res_model) or (action.src_model and not pool.get(action.src_model))):
            to_unlink.append(action.id)
            log.info("Cannot find model %s or %s, removing associated act_window" % (action.res_model, action.src_model))
    obj.unlink(cr, 1, to_unlink)

def mgr_res_users(cr):
    # you cannot have a menu action as home action anymore
    # this causes an infinite loop in the web client
    cr.execute(
        "UPDATE res_users SET action_id = NULL " +
        "FROM ir_actions WHERE action_id = ir_actions.id " +
        "AND ir_actions.usage = 'menu'"
        )

def migrate(cr, version):
    try:
        
        log.info("post-set-defaults.py now called")
    
        # this method called in a try block too
        pool = pooler.get_pool(cr.dbname)

        mgr_clean_act_window(cr, pool)
        for model in defaults.keys():
            set_default(cr, pool, model, defaults[model])

        mgr_ir_rule(cr, pool)
        mgr_res_partner_address(cr, pool)
        mgr_res_partner(cr, pool)
        mgr_default_bank(cr, pool)
        mgr_roles_to_groups(cr, pool)
        mgr_res_currency(cr, pool)
        mgr_ir_module_module(cr)
        mgr_res_users(cr)
    except Exception, e:
        log.info("Migration: error in post-set-defaults.py: %s" % e)
        raise

