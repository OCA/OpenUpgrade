# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def remove_noupdate_records(env):
    """Remove deleted noupdate records."""
    xml_ids = [
        'hr_contract.rule_contract_1_set_as_pending',
        'hr_contract.rule_contract_2_set_as_pending',
        'hr_contract.rule_contract_3_set_as_close',
        'hr_contract.rule_contract_4_set_as_close',
        'hr_contract.contract_set_as_close',
        'hr_contract.contract_set_as_pending',
        'hr_contract.ir_cron_data_contract_update_state',
        'hr_contract.contract_open',
    ]
    for xml_id in xml_ids:
        try:
            record = env.ref(xml_id)
            record.unlink()
        except Exception:  # pragma: no cover
            pass


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    remove_noupdate_records(env)
