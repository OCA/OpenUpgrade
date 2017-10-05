# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Remove security rule
    rule_xml_ids = ('resource_own_leaves',)
    env.cr.execute(
        """ DELETE FROM ir_rule WHERE id IN (
                SELECT res_id FROM ir_model_data WHERE module = 'resource'
                    AND name IN %s)
        """, (rule_xml_ids,))
    env.cr.execute(
        """ DELETE FROM ir_model_data WHERE module = 'resource'
                AND name IN %s)
        """, (rule_xml_ids,))
