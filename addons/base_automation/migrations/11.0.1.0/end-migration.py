# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def deactivate_invalid_model_rules(env):
    """Deactivate rules with invalid models."""
    for rule in env['base.automation'].search([]):
        if not env.get(rule.model_name):
            rule.active = False


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    deactivate_invalid_model_rules(env)
