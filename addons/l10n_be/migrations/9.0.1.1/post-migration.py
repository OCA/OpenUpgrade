# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV - Stéphane Bidoul
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import csv
import logging
import os

from openerp import SUPERUSER_ID
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


MIG_TAX_LINE_PREFIX = "[8 to 9 tax migration] "
MIG_TAX_PREFIX = "Mig Code "


def _load_code2tag(env):
    res = {}
    here = os.path.dirname(__file__)
    with open(os.path.join(here, 'tax_code2tag.csv')) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        header = next(reader)
        code_code_index = header.index('account.tax.code:code')
        tag_xmlid_index = header.index('account.account.tag:xmlid')
        ttype_index = header.index('ttype')
        dc_index = header.index('sign')
        for row in reader:
            code_code = row[code_code_index]
            tag_xmlid = row[tag_xmlid_index]
            ttype = row[ttype_index]
            dc = row[dc_index]
            if not code_code:
                continue
            if tag_xmlid:
                res[code_code] = (env.ref(tag_xmlid), ttype, dc)
            else:
                res[code_code] = (None, None, None)
    return res


def _load_codeid2code(env):
    res = {}
    env.cr.execute("""
       SELECT id, code FROM account_tax_group
    """)
    for code_id, code_code in env.cr.fetchall():
        res[code_id] = code_code
    return res


def _create_tax_from_tax_code(env, company_id, tax_code_id, codeid2tag):
    """ Create an inactive tax that is linked to a single tax tag
    correponding to the provided tax_code_id.
    """
    tax_tag, _, _ = codeid2tag.get(tax_code_id)
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
        'type_tax_use': 'none',
        'amount_type': 'group',
        'amount': 0,
    })
    _logger.info(
        "Created tax '%s' with tag '%s'",
        tax.name, tax_tag.name,
    )
    return tax


def _get_tax_from_tax_code(env, company_id, tax_code_id, codeid2tag, tc2t):
    """ Obtain a tax corresponding to the provided tax_code_id

    Return tax_id, tax type ('base' or 'tax' or None), 'deb' or 'crd'
    """
    if tax_code_id in tc2t:
        return tc2t[tax_code_id]

    _, ttype, dc = codeid2tag.get(tax_code_id)

    tax = _create_tax_from_tax_code(
        env, company_id, tax_code_id, codeid2tag,
    )
    tax_id = tax.id if tax else None
    tc2t[tax_code_id] = (tax_id, ttype, dc)

    return tax_id, ttype, dc


def set_aml_taxes(env, company_id, codeid2tag):
    tc2t = {}
    _logger.info("set_aml_taxes step for company %s", company_id)
    env.cr.execute(
        """SELECT aml.*
        FROM account_move_line aml
        WHERE aml.company_id=%s
          AND aml.tax_code_id IS NOT NULL
        """, (company_id, )
    )
    for row in env.cr.dictfetchall():
        tax_id, ttype, dc = _get_tax_from_tax_code(
            env, company_id, row['tax_code_id'], codeid2tag, tc2t,
        )
        if not tax_id:
            # the error has been logged before
            _logger.error("tax code %s not found", row['tax_code_id'])
        assert ttype
        if dc == 'deb':
            if row['tax_amount'] > 0:
                wanted_debit = row['tax_amount']
                wanted_credit = 0
            else:
                wanted_debit = 0
                wanted_credit = -row['tax_amount']
        elif dc == 'crd':
            if row['tax_amount'] > 0:
                wanted_debit = 0
                wanted_credit = row['tax_amount']
            else:
                wanted_debit = -row['tax_amount']
                wanted_credit = 0
        else:
            _logger.error("error: unknown dc %s for tax code %s", dc, row['tax_code_id'])
            continue
        if ttype == 'base':
            if row['debit'] == wanted_debit and row['credit'] == wanted_credit:
                base_ml = row
            else:
                # it's a base, add the tax to another move line
                # with the same amount
                env.cr.execute(
                    """SELECT id
                    FROM account_move_line
                    WHERE move_id=%s
                      AND debit=%s AND credit=%s
                      AND tax_code_id IS NOT NULL
                      AND tax_line_id IS NULL
                    """, (row['move_id'], wanted_debit, wanted_credit)
                )
                base_ml = env.cr.dictfetchall()
                if base_ml:
                    base_ml = base_ml[0]
            if base_ml:
                openupgrade.logged_query(
                    env.cr,
                    """INSERT INTO account_move_line_account_tax_rel
                    (account_move_line_id, account_tax_id)
                    SELECT %s, %s
                    WHERE NOT EXISTS (
                        SELECT * FROM account_move_line_account_tax_rel
                        WHERE account_move_line_id=%s AND account_tax_id=%s
                    )
                    RETURNING account_move_line_id
                    """, (base_ml['id'], tax_id, base_ml['id'], tax_id)
                )
                if env.cr.fetchone():
                    # if we could insert, it's ok, continue the loop
                    # if not, it means we have several similar line and
                    # we must create dummy debit/credit lines to hold the tax
                    continue
            else:
                # we'll add a dummy line to hold the tax with the correct debit/credit
                pass
        elif ttype == 'tax':
            if row['debit'] == wanted_debit and row['credit'] == wanted_credit:
                tax_ml = row
            else:
                tax_ml = None
            if tax_ml:
                openupgrade.logged_query(
                    env.cr,
                    """UPDATE account_move_line
                    SET tax_line_id = %s
                    WHERE id=%s
                    """, (tax_id, tax_ml['id'])
                )
                continue
            else:
                # we'll add a dummy line to hold the tax with the correct debit/credit
                pass

        # we did not find a move line with same debit/credit/tax_code_id
        # create new debit/credit lines to hold the tax information
        for d, c, t in (
                (wanted_debit, wanted_credit, tax_id),
                (wanted_credit, wanted_debit, None),
        ):
            rec = row.copy()
            rec.pop('id')
            rec.pop('create_date')
            rec.pop('create_uid')
            rec.pop('write_date')
            rec.pop('write_uid')
            rec.pop('tax_amount')
            rec.pop('tax_code_id')
            rec['create_uid'] = SUPERUSER_ID
            rec['debit'] = d
            rec['credit'] = c
            rec['balance'] = d - c 
            rec['tax_line_id'] = t if (t and ttype == 'tax') else None
            rec['name'] = MIG_TAX_LINE_PREFIX + rec['name']
            columns = list(rec.keys())
            values = ["%({})s".format(c) for c in columns]
            openupgrade.logged_query(
                env.cr,
                """INSERT INTO account_move_line
                ({}) VALUES ({})
                RETURNING id
                """.format(
                    ",".join(columns),
                    ",".join(values),
                ),
                rec,
            )
            if t and ttype == 'base':
                new_ml_id = env.cr.fetchone()[0]
                openupgrade.logged_query(
                    env.cr,
                    """INSERT INTO account_move_line_account_tax_rel
                    (account_move_line_id, account_tax_id)
                    VALUES (%s, %s)
                    """, (new_ml_id, tax_id)
                )


def reset_aml_taxes(env, company_id):
    _logger.info("clearing aml.tax_line_id")
    openupgrade.logged_query(
        env.cr,
        """UPDATE account_move_line
        SET tax_line_id = NULL
        WHERE tax_line_id IS NOT NULL
          AND company_id = %s
        """, (company_id, )
    )
    _logger.info("clearing aml.tax_ids")
    openupgrade.logged_query(
        env.cr,
        """DELETE FROM account_move_line_account_tax_rel
        WHERE account_move_line_id IN
          (SELECT id FROM account_move_line
           WHERE company_id=%s)
        """, (company_id, )
    )
    _logger.info("deleting %s taxes", MIG_TAX_PREFIX)
    openupgrade.logged_query(
        env.cr,
        """DELETE FROM account_tax
        WHERE name LIKE '{}%%'
          AND company_id = %s
        """.format(MIG_TAX_PREFIX),
        (company_id, )
    )
    _logger.info("deleting %s aml", MIG_TAX_LINE_PREFIX)
    openupgrade.logged_query(
        env.cr,
        """DELETE FROM account_move_line
        WHERE name LIKE '{}%%'
          AND company_id = %s
        """.format(MIG_TAX_LINE_PREFIX),
        (company_id, )
    )
    env.cr.commit()


def _migrate(env):
    code2tag = _load_code2tag(env)
    codeid2code = _load_codeid2code(env)
    codeid2tag = {}
    for codeid, code in codeid2code.items():
        codeid2tag[codeid] = code2tag.get(code)
    for company in env['res.company'].search([]):
        if company.partner_id.country_id.code != 'BE':
            continue
        reset_aml_taxes(env, company.id)
        set_aml_taxes(env, company.id, codeid2tag)


@openupgrade.migrate(use_env=True, no_version=True)
def migrate(env, version):
    _migrate(env)
