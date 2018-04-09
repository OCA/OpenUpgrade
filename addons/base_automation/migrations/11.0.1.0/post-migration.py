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
        if not field:
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
        env.cr.execute(
            """SELECT res_partner_id
            FROM base_action_rule_res_partner_rel
            WHERE base_action_rule_id = %s"""
        )
        new_rule.write({
            'state': 'followers',
            'partner_ids': [
                (6, 0, [x[0] for x in env.cr.fetchall()]),
            ]
        })


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    migrate_act_user_id(env)
    migrate_act_followers(env)
