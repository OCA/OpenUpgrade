# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def migrate_act_user_id(env):
    """Migrate action rules that have field act_user_id filled for assigning
    a responsible, creating/updating the rule and adding the field
    """
    BaseAutomation = env['base.automation']
    IrModelFields = env['ir.model.fields']
    env.cr.execute(
        "SELECT id, act_user_id "
        "FROM base_automation "
        "WHERE act_user_id IS NOT NULL"
    )
    for row in env.cr.fetchall():
        rule = BaseAutomation.browse(row[0])
        field = IrModelFields.search([
            ('name', '=', 'user_id'),
            ('model_id', '=', rule.model_id.id),
        ])
        if not field:  # pragma: no cover
            continue
        if rule.child_ids:
            # If the rule has server actions to run, duplicate it
            new_rule = rule.copy({'child_ids': False})
        else:
            new_rule = rule
        new_rule.write({
            'state': 'object_write',
            'fields_lines': [
                (0, 0, {
                    'col1': field.id,
                    'type': 'value',
                    'value': row[1],
                }),
            ]
        })


def migrate_act_followers(env):
    """Migrate action rules that have field act_followers filled for adding
    followers, creating/updating the rule and setting the new m2m.
    """
    BaseAutomation = env['base.automation']
    env.cr.execute(
        """SELECT DISTINCT(ba.id)
        FROM base_automation ba,
            base_action_rule_res_partner_rel rel
        WHERE rel.base_action_rule_id = ba.id"""
    )
    for row in env.cr.fetchall():
        rule = BaseAutomation.browse(row[0])
        if rule.child_ids or rule.state != 'multi':
            # If the rule has server actions to run or has been used already
            # assigning a responsible, duplicate it
            new_rule = rule.copy({'child_ids': False})
        else:
            new_rule = rule
        # Update through SQL this value, as there's a check that rises an
        # error, as models haven't loaded yet the inheritance from mail.thread
        env.cr.execute(
            "UPDATE ir_act_server SET state = 'followers' WHERE id = %s",
            (new_rule.action_server_id.id, ),
        )
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO ir_act_server_res_partner_rel
            (ir_act_server_id, res_partner_id)
            SELECT %s, rel.res_partner_id
            FROM base_action_rule_res_partner_rel rel
            WHERE rel.base_action_rule_id = %s
            """, (new_rule.action_server_id.id, row[0]),
        )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    migrate_act_user_id(env)
    migrate_act_followers(env)
