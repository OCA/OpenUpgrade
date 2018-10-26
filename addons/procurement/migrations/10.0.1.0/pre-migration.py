# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _delete_views(env):
    views = [
        'procurement.mrp_company',
    ]
    openupgrade.delete_records_safely_by_xml_id(
        env,
        views,
    )


@openupgrade.migrate()
def migrate(env, version):
    _delete_views(env)
