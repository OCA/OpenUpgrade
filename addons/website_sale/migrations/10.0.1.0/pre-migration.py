# -*- coding: utf-8 -*-
# © 2017 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    # keeping info in website pricelist table that would be dropped
    sql = """create table website_pricelist_openupgrade_10 as select * from
        website_pricelist"""
    cr.execute(sql)
