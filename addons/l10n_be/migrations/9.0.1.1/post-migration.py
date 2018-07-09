# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV - Stéphane Bidoul
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import csv
import logging
import os

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


MIG_TAX_PREFIX = "Mig Code "
MIG_TAX_LINE_PREFIX = "[9 to 9 tax migration] "


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


def set_tax_tags_from_tax_codes(env, company_id, codeid2tag):
    taxes = env['account.tax'].search([
        ('company_id', '=', company_id),
    ])
    for tax in taxes:
        tags = []
        env.cr.execute("""
            SELECT
              base_code_id, tax_code_id,
              ref_base_code_id, ref_tax_code_id
            FROM account_tax
            WHERE id = %s
        """, (tax.id, ))
        for code_id in env.cr.fetchone():
            if not code_id:
                continue
            tag = codeid2tag.get(code_id)
            if tag:
                tags.append(tag)
            else:
                _logger.error(
                    "Tax %s [%s] references tax code %s which does "
                    "not map to a tax tag. You need to resolve this "
                    "manually.",
                    tax.name, tax.id, code_id,
                )
        tax.write({
            'tag_ids': [(6, 0, [t.id for t in tags])],
        })


def _create_tax_from_tax_code(env, company_id, tax_code_id, codeid2tag):
    tax_tag = codeid2tag.get(tax_code_id)
    if not tax_tag:
        _logger.error(
            "Tax code with id [%s] does "
            "not map to a tax tag. You need to resolve this "
            "manually.",
            tax_code_id,
        )
        return None
    env.cr.execute(
        """SELECT code FROM account_tax_group WHERE id=%s""",
        (tax_code_id, )
    )
    tax_code_code = env.cr.fetchone()[0]
    tax = env['account.tax'].create({
        'name': MIG_TAX_PREFIX + tax_code_code,
        'company_id': company_id,
        'tag_ids': [(6, 0, [tax_tag.id])],
        'active': False,
        'amount': 0,
    })
    _logger.info(
        "Created tax '%s' with tag '%s'",
        tax.name, tax_tag.name,
    )
    return tax


def _get_tax_from_tax_code(env, company_id, tax_code_id, codeid2tag, tc2t):
    if tax_code_id in tc2t:
        return tc2t[tax_code_id]
    env.cr.execute(
        """SELECT id FROM account_tax
        WHERE base_code_id=%(tax_code_id)s
        OR ref_base_code_id=%(tax_code_id)s""",
        {'tax_code_id': tax_code_id},
    )
    base_tax_ids = env.cr.fetchall()
    env.cr.execute(
        """SELECT id FROM account_tax
        WHERE tax_code_id=%(tax_code_id)s
        OR ref_tax_code_id=%(tax_code_id)s""",
        {'tax_code_id': tax_code_id},
    )
    tax_tax_ids = env.cr.fetchall()
    if base_tax_ids and not tax_tax_ids:
        ttype = 'base'
    elif tax_tax_ids and not base_tax_ids:
        ttype = 'tax'
    else:
        ttype = None
    tax_ids = base_tax_ids + tax_tax_ids
    if len(tax_ids) == 1:
        tax_id = tax_ids[0]
    else:
        tax = _create_tax_from_tax_code(
            env, company_id, tax_code_id, codeid2tag,
        )
        tax_id = tax.id if tax else None
    tc2t[tax_code_id] = (tax_id, ttype)
    return tax_id, ttype


def set_aml_taxes(env, company_id, codeid2tag):
    env.cr.execute(
        """SELECT DISTINCT tax_code_id
        FROM account_move_line
        WHERE company_id=%s 
          AND tax_code_id IS NOT NULL
          AND (debit != 0 or credit != 0) AND tax_amount != 0
        """, (company_id, )
    )
    tc2t = {}
    for tax_code_id, in env.cr.fetchall():
        tax_id, ttype = _get_tax_from_tax_code(
            env, company_id, tax_code_id, codeid2tag, tc2t,
        )
        if not tax_id:
            continue
        if ttype == 'tax':
            env.cr.execute(
                """UPDATE account_move_line
                SET tax_line_id=%s
                WHERE tax_code_id=%s
                  AND (debit != 0 or credit != 0) AND tax_amount != 0
                """, (tax_id, tax_code_id)
            )
        elif ttype == 'base':
            env.cr.execute(
                """INSERT INTO account_move_line_account_tax_rel
                (account_move_line_id, account_tax_id)
                SELECT id, %s
                FROM account_move_line
                WHERE tax_code_id=%s
                  AND (debit != 0 or credit != 0) AND tax_amount != 0
                """,
                (tax_id, tax_code_id)
            )
        else:
            _logger.error(
                "account.tax.code %s may correspond to both base and taxes. "
                "You need to fix move lines with this tax_code_id manually "
                "by finding a way to determine if it's a base or tax "
                "and set tax_ids or tax_line_id to %s.",
                tax_code_id, tax_id,
            )
    env.cr.execute(
        """SELECT id, date, name, move_id, account_id, tax_code_id, tax_amount
        FROM account_move_line
        WHERE company_id=%s
          AND tax_code_id IS NOT NULL
          AND debit = 0 AND credit = 0 AND tax_amount != 0
        """, (company_id, )
    )
    for ml_id, date, name, move_id, account_id, tax_code_id, tax_amount \
            in env.cr.fetchall():
        tax_id, ttype = _get_tax_from_tax_code(
            env, company_id, tax_code_id, codeid2tag, tc2t,
        )
        if not tax_id:
            continue
        if tax_amount < 0:
            debit = -tax_amount
            credit = 0
        else:
            debit = 0
            credit = tax_amount
        for d, c, t in ((debit, credit, tax_id), (credit, debit, None)):
            env.cr.execute(
                """INSERT INTO account_move_line
                (move_id, date, date_maturity, name,
                 account_id, debit, credit, tax_line_id)
                VALUES
                (%s, %s, %s, %s,
                 %s, %s, %s, %s)
                """, (move_id, date, date, MIG_TAX_LINE_PREFIX + name,
                      account_id, d, c, t)
            )


def reset_aml_taxes(env, company_id):
    env.cr.execute("""
        UPDATE account_move_line
        SET tax_line_id = NULL
        WHERE tax_line_id IS NOT NULL
          AND company_id = %s
    """, (company_id, ))
    env.cr.execute("""
        DELETE FROM account_move_line_account_tax_rel
        WHERE account_move_line_id IN
          (SELECT id FROM account_move_line
           WHERE company_id=%s)
    """, (company_id, ))
    env.cr.execute(
        """DELETE FROM account_tax
        WHERE name LIKE '{}%'
        """.format(MIG_TAX_PREFIX),
    )
    env.cr.execute(
        """DELETE FROM account_move_line
        WHERE name LIKE %s || '%'
        """, (MIG_TAX_LINE_PREFIX, )
    )


def _migrate(env):
    code2tag = _load_code2tag(env)
    codeid2code = _load_codeid2code(env)
    codeid2tag = {}
    for codeid, code in codeid2code.items():
        codeid2tag[codeid] = code2tag.get(code)
    for company in env['res.company'].search([]):
        if company.partner_id.country_id.code != 'BE':
            continue
        set_tax_tags_from_tax_codes(env, company.id, codeid2tag)
        # reset_aml_taxes(env, company.id)
        set_aml_taxes(env, company.id, codeid2tag)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    _migrate(env)


_migrate(env)
