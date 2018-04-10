# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_contract_company(env):
    """Put the company of the job in the contract."""
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_contract hc
        SET company_id = hj.company_id
        FROM hr_job hj
        WHERE hc.job_id = hj.id
        AND hj.company_id IS NOT NULL
        """
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    update_contract_company(env)
