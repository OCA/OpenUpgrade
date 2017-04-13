# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    # create an xmlid for mail.bounce.alias is it exists
    cr.execute(
        """insert into ir_model_data
        (module, name, model, res_id)
        select 'mail', 'icp_mail_bounce_alias', 'ir.config_parameter', id
        from ir_config_parameter
        where key='mail.bounce.alias' limit 1"""
    )
