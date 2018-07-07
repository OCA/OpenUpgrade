# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV - Stéphane Bidoul
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from __future__ import print_function
import csv
import logging
import os

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _load_code2tag(env):
    res = {}
    here = os.path.dirname(__file__)
    with open(os.path.join(here, 'tax_code2tag.csv')) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        header = next(reader)
        code_code_index = header.index('account.tax.code:code')
        tag_xmlid_index = header.index('account.account.tag:xmlid')
        for row in reader:
            code_code = row[code_code_index]
            tag_xmlid = row[tag_xmlid_index]
            if not code_code:
                continue
            if tag_xmlid:
                res[code_code] = env.ref(tag_xmlid)
            else:
                res[code_code] = None
    return res


def _load_codeid2code(env):
    res = {}
    env.cr.execute("""
       SELECT id, code FROM account_tax_group
    """)
    for code_id, code_code in env.cr.fetchall():
        res[code_id] = code_code
    return res


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    code2tag = _load_code2tag(env)
    codeid2code = _load_codeid2code(env)
    for company in env['res.company'].search([]):
        if company.partner_id.country_id.code != 'BE':
            continue
        taxes = env['account.tax'].search([
            ('company_id', '=', company.id),
        ])
        for tax in taxes:
            tags = []
            cr.execute("""
                SELECT
                  base_code_id, tax_code_id,
                  ref_base_code_id, ref_tax_code_id
                FROM account_tax
                WHERE id = %s
            """, (tax.id, ))
            for code_id in cr.fetchone():
                if not code_id:
                    continue
                code_code = codeid2code[code_id]
                if code2tag.get(code_code):
                    tags.append(code2tag[code_code])
                else:
                    _logger.error(
                        "Tax %s [%s] references tax code %s which does "
                        "not map to a tax tag. You need to resolve this "
                        "manually.",
                        tax.name, tax.id, code_code,
                    )
            tax.write({
                'tag_ids': [(6, 0, [tag.id for tag in tags])],
            })
