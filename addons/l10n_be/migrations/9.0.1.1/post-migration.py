# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV - Stéphane Bidoul
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import csv
import logging
import os

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


MIG_TAX_LINE_PREFIX = "[8 to 9 tax migration] "

# Set this to True if you want to attempt to reuse existing taxes
# on move lines. If False, a new inactive tax is created for each
# tax code used on move lines.
MIG_TAX_REUSE = False
MIG_TAX_PREFIX = "Mig Code "


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
    """ Create an inactive tax that is linked to a single tax tag
    correponding to the provided tax_code_id.
    """
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


def _get_tax_from_tax_code(env, company_id, tax_code_id, inv_type,
                           codeid2tag, tc2t):
    """ Obtain a tax corresponding to the providing tax_code_id
    and invoice type. Try to determine if this tax code is
    used as base or tax.

    Return tax_id, tax type ('base' or 'tax' or None)
    """
    if (tax_code_id, inv_type) in tc2t:
        return tc2t[(tax_code_id, inv_type)]
    #
    # 1. find out ttype (base or tax)
    #
    base_where = []
    tax_where = []
    if inv_type == 'in_invoice':
        base_where.append(
            "base_code_id=%(tax_code_id)s AND "
            "type_tax_use='purchase'"
        )
        tax_where.append(
            "tax_code_id=%(tax_code_id)s AND "
            "type_tax_use='purchase'"
        )
    elif inv_type == 'out_invoice':
        base_where.append(
            "base_code_id=%(tax_code_id)s AND "
            "type_tax_use='sale'"
        )
        tax_where.append(
            "tax_code_id=%(tax_code_id)s AND "
            "type_tax_use='sale'"
        )
    elif inv_type == 'in_refund':
        base_where.append(
            "ref_base_code_id=%(tax_code_id)s AND "
            "type_tax_use='purchase'"
        )
        tax_where.append(
            "ref_tax_code_id=%(tax_code_id)s AND "
            "type_tax_use='purchase'"
        )
    elif inv_type == 'out_refund':
        base_where.append(
            "ref_base_code_id=%(tax_code_id)s AND "
            "type_tax_use='sale'"
        )
        tax_where.append(
            "ref_tax_code_id=%(tax_code_id)s AND "
            "type_tax_use='sale'"
        )
    else:
        base_where.append(
            "base_code_id=%(tax_code_id)s OR "
            "ref_base_code_id=%(tax_code_id)s"
        )
        tax_where.append(
            "tax_code_id=%(tax_code_id)s OR "
            "ref_tax_code_id=%(tax_code_id)s"
        )
    base_where = base_where[0]
    env.cr.execute(
        "SELECT id FROM account_tax WHERE " + base_where,
        {'tax_code_id': tax_code_id},
    )
    base_tax_ids = env.cr.fetchall()
    tax_where = tax_where[0]
    env.cr.execute(
        "SELECT id FROM account_tax WHERE " + tax_where,
        {'tax_code_id': tax_code_id},
    )
    tax_tax_ids = env.cr.fetchall()
    if base_tax_ids and not tax_tax_ids:
        ttype = 'base'
    elif tax_tax_ids and not base_tax_ids:
        ttype = 'tax'
    else:
        # this code can be used as base or tax
        ttype = None
    #
    # 2. find out tax or create a new one
    #
    tax_ids = base_tax_ids + tax_tax_ids
    if MIG_TAX_REUSE and len(tax_ids) == 1:
        tax_id = tax_ids[0]
    else:
        if MIG_TAX_REUSE and not tax_ids:
            _logger.warning(
                "No tax found using tax_code_id [%s] and invoice "
                "type '%s', creating one.",
                tax_code_id, inv_type,
            )
        # several taxes use this code, create one
        # and cache those we have created
        if (tax_code_id, 'mig') in tc2t:
            tax_id = tc2t[(tax_code_id, 'mig')]
        else:
            tax = _create_tax_from_tax_code(
                env, company_id, tax_code_id, codeid2tag,
            )
            tax_id = tax.id if tax else None
            tc2t[(tax_code_id, 'mig')] = tax_id
    tc2t[(tax_code_id, inv_type)] = (tax_id, ttype)
    return tax_id, ttype


def set_aml_taxes(env, company_id, codeid2tag):
    tc2t = {}
    ambiguous_tax_codes = []
    #
    # Step 1.
    # 
    # Handle the normal case: debit or credit != 0 and tax amount != 0
    #
    # * If the tax code can be unambiguously linked to a tax for use
    #   as tax amount, use it for tax_line_id.
    # * If the tax code can be unambiguously linked to a tax for use
    #   as base amount, us it for tax_ids
    #
    # If the tax code may be used for base or tax, keep it
    # a list of ambiguous tax code that we'll attempt to diambiguate
    # in step 2.
    #
    env.cr.execute(
        """SELECT DISTINCT tax_code_id, inv.type
        FROM account_move_line aml
        LEFT JOIN account_invoice inv on inv.id = aml.invoice_id
        WHERE aml.company_id=%s
          AND aml.tax_code_id IS NOT NULL
          AND (aml.debit != 0 or aml.credit != 0) AND aml.tax_amount != 0
        """, (company_id, )
    )
    for tax_code_id, inv_type, in env.cr.fetchall():
        _logger.info("tax code [%s] '%s'", tax_code_id, inv_type)
        tax_id, ttype = _get_tax_from_tax_code(
            env, company_id, tax_code_id, inv_type, codeid2tag, tc2t,
        )
        if not tax_id:
            # the error has been logged before
            continue
        if ttype == 'tax':
            if not inv_type:
                env.cr.execute(
                    """UPDATE account_move_line
                    SET tax_line_id=%s
                    WHERE tax_code_id=%s
                      AND (debit != 0 or credit != 0) AND tax_amount != 0
                      AND invoice_id IS NULL
                    """, (tax_id, tax_code_id)
                )
            else:
                env.cr.execute(
                    """UPDATE account_move_line
                    SET tax_line_id=%s
                    WHERE tax_code_id=%s
                      AND (debit != 0 or credit != 0) AND tax_amount != 0
                      AND invoice_id IN 
                          (SELECT id FROM account_invoice
                           WHERE type=%s AND company_id=%s)
                    """, (tax_id, tax_code_id, inv_type, company_id)
                )
        elif ttype == 'base':
            if not inv_type:
                env.cr.execute(
                    """INSERT INTO account_move_line_account_tax_rel
                    (account_move_line_id, account_tax_id)
                    SELECT aml.id, %s
                    FROM account_move_line aml
                    WHERE aml.tax_code_id=%s
                      AND invoice_id IS NULL
                      AND (debit != 0 or credit != 0) AND tax_amount != 0
                    """,
                    (tax_id, tax_code_id)
                )
            else:
                env.cr.execute(
                    """INSERT INTO account_move_line_account_tax_rel
                    (account_move_line_id, account_tax_id)
                    SELECT aml.id, %s
                    FROM account_move_line aml
                    LEFT JOIN account_invoice inv ON inv.id = aml.invoice_id
                    WHERE aml.tax_code_id=%s
                      AND inv.type=%s
                      AND (debit != 0 or credit != 0) AND tax_amount != 0
                    """,
                    (tax_id, tax_code_id, inv_type)
                )
        else:
            if not inv_type:
                _logger.error(
                    "account.tax.group %s may correspond to both base and "
                    "taxes. You need to manually fix move lines that have "
                    "this tax_code_id and are not related to an invoice "
                    "by finding a way to determine if it's a base or tax "
                    "and set tax_ids or tax_line_id to %s.",
                    tax_code_id, tax_id,
                )
            else:
                ambiguous_tax_codes.append((tax_code_id, inv_type))
    #
    # Step 2.
    #
    # Handle ambiguous tax codes by looking at the invoice linked
    # to the move line and examine the account_invoice_tax table
    # to determine if the tax code is for base or tax.
    # If this fails, log an error (this should be very rare).
    #
    for tax_code_id, inv_type in ambiguous_tax_codes:
        _logger.info(
            "Trying to disambiguate tax code [%s] '%s'.",
            tax_code_id, inv_type,
        )
        env.cr.execute(
            """SELECT aml.id, aml.date, aml.name, aml.move_id,
                      aml.account_id, aml.tax_code_id, aml.tax_amount,
                      invoice_id, inv.type
            FROM account_move_line aml
            LEFT JOIN account_invoice inv ON inv.id = aml.invoice_id
            WHERE tax_code_id=%s AND inv.type=%s
            """, (tax_code_id, inv_type)
        )
        for ml_id, date, name, move_id, \
                account_id, tax_code_id, tax_amount, \
                invoice_id, inv_type \
                in env.cr.fetchall():
            if not invoice_id:
                _logger.error(
                    "Could not determine if tax code [%s] is base or tax for "
                    "move line %s [%s] because it is not linked to an invoice. "
                    "You need to fix this manually.",
                    tax_code_id, name, ml_id, invoice_id,
                )
                continue
            env.cr.execute(
                """SELECT base_amount, base_code_id, tax_amount, tax_code_id
                FROM account_invoice_tax
                WHERE invoice_id=%s
                """ % (invoice_id, )
            )
            invoice_taxes = env.cr.fetchall()
            ttype = None
            in_bases = any(x == tax_code_id for _, x, _, _ in invoice_taxes)
            in_taxes = any(x == tax_code_id for _, _, _, x in invoice_taxes)
            if in_bases and not in_taxes:
                ttype = 'base'
            elif in_taxes and not in_bases:
                ttype = 'tax'
            else:
                for inv_base_amount, inv_base_code_id, \
                        inv_tax_amount, inv_tax_code_id \
                        in invoice_taxes:
                    if inv_base_amount == tax_amount and \
                            inv_base_code_id == tax_code_id:
                        ttype = 'base'
                        break
                    elif inv_tax_amount == tax_amount and \
                            inv_tax_code_id == tax_code_id:
                        ttype = 'tax'
                        break
            tax_id, _ = _get_tax_from_tax_code(
                env, company_id, tax_code_id, inv_type, codeid2tag, tc2t,
            )
            if not tax_id:
                # the error has been logged before
                continue
            if ttype == 'tax':
                _logger.warning(
                    "Found a move line [%s] with a tax code that could be "
                    "base or tax, and which is actually a tax, "
                    "This will be handled correctly but we log it "
                    "as it should be a rare occurence.",
                    ml_id,
                )
                env.cr.execute(
                    """UPDATE account_move_line
                    SET tax_line_id=%s
                    WHERE id=%s
                    """, (tax_id, ml_id)
                )
            elif ttype == 'base':
                env.cr.execute(
                    """INSERT INTO account_move_line_account_tax_rel
                    (account_move_line_id, account_tax_id)
                    VALUES (%s, %s)
                    """,
                    (ml_id, tax_id)
                )
            else:
                _logger.error(
                    "Could not determine if tax code [%s] is base or tax for "
                    "move line %s [%s] of invoice [%s]. "
                    "You need to fix this manually.",
                    tax_code_id, name, ml_id, invoice_id,
                )
    #
    # Step 3.
    #
    # Handle tax lines with debit=credit=0 by creating debit/credit transaction
    #
    # If it's a base we try to find the base line in the same move with
    # same amount and add the tax to it. If we don't find it, or if it's a tax,
    # we create new move lines.
    #
    env.cr.execute(
        """SELECT aml.id, aml.date, aml.name, aml.move_id,
                  aml.account_id, aml.tax_code_id, aml.tax_amount,
                  inv.type
        FROM account_move_line aml
        LEFT JOIN account_invoice inv ON inv.id = aml.invoice_id
        WHERE aml.company_id=%s
          AND aml.tax_code_id IS NOT NULL
          AND aml.debit = 0 AND aml.credit = 0 AND aml.tax_amount != 0
        """, (company_id, )
    )
    for ml_id, date, name, move_id, \
            account_id, tax_code_id, tax_amount, \
            inv_type \
            in env.cr.fetchall():
        tax_id, ttype = _get_tax_from_tax_code(
            env, company_id, tax_code_id, inv_type, codeid2tag, tc2t,
        )
        if not tax_id:
            # the error has been logged before
            continue
        if not ttype:
            _logger.error(
                "account.tax.code %s may correspond to both base and taxes "
                "for move line %s [%s] with invoice type '%s'. "
                "You need to fix move lines with this tax_code_id manually "
                "by finding a way to determine if it's a base or tax "
                "and set tax_ids or tax_line_id to %s.",
                tax_code_id, name, ml_id, inv_type, tax_id,
            )
        elif ttype == 'tax':
            _logger.warning(
                "Found a move line [%s] with a tax code that could be "
                "base or tax, and which is actually a tax, "
                "This will be handled correctly but we log it "
                "as it should be a rare occurence.",
                ml_id,
            )
        if tax_amount < 0:
            debit = -tax_amount
            credit = 0
        else:
            debit = 0
            credit = tax_amount
        if ttype == 'none':
            _logger.error(
                "account.tax.code %s may correspond to both base and taxes "
                "on move line [%s]. "
                "You need to fix move lines with this tax_code_id manually "
                "by finding a way to determine if it's a base or tax "
                "and set tax_ids or tax_line_id to [%s].",
                tax_code_id, tax_id,
            )
            continue
        if ttype == 'base':
            # it's a base, add the tax to another move line
            # with the same amount
            env.cr.execute(
                """SELECT id
                FROM account_move_line
                WHERE move_id=%s
                  AND debit=%s AND credit=%s
                  AND tax_code_id != %s
                  AND tax_line_id IS NULL
                """, (move_id, debit, credit, tax_code_id)
            )
            base_ml = env.cr.fetchall()
            if base_ml:
                env.cr.execute(
                    """INSERT INTO account_move_line_account_tax_rel
                    (account_move_line_id, account_tax_id)
                    VALUES (%s, %s)
                    """, (base_ml[0], tax_id)
                )
                continue
        # we did not find a move line with same debit/credit/tax_code_id
        # create new debit/credit lines
        vals = []
        for d, c, t in ((debit, credit, tax_id), (credit, debit, None)):
            vals.append((0, 0, dict(
                date=date,
                date_maturity=date,
                name=MIG_TAX_LINE_PREFIX + name,
                account_id=account_id,
                debit=d,
                credit=c,
                tax_line_id=t if t and ttype == 'tax' else False,
                tax_ids=[(6, 0, [tax_id] if t and ttype == 'base' else [])],
            )))
        _logger.debug("updating move %s for 0/0/tax", move_id)
        env['account.move'].browse(move_id).write(dict(line_ids=vals))


def reset_aml_taxes(env, company_id):
    _logger.info("clearing aml.tax_line_id")
    env.cr.execute(
        """UPDATE account_move_line
        SET tax_line_id = NULL
        WHERE tax_line_id IS NOT NULL
          AND company_id = %s
        """, (company_id, )
    )
    _logger.info("clearing aml.tax_ids")
    env.cr.execute(
        """DELETE FROM account_move_line_account_tax_rel
        WHERE account_move_line_id IN
          (SELECT id FROM account_move_line
           WHERE company_id=%s)
        """, (company_id, )
    )
    _logger.info("deleting %s taxes", MIG_TAX_PREFIX)
    env.cr.execute(
        """DELETE FROM account_tax
        WHERE name LIKE '{}%%'
          AND company_id = %s
        """.format(MIG_TAX_PREFIX),
        (company_id, )
    )
    _logger.info("deleting %s aml", MIG_TAX_LINE_PREFIX)
    env.cr.execute(
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
        set_tax_tags_from_tax_codes(env, company.id, codeid2tag)
        reset_aml_taxes(env, company.id)
        set_aml_taxes(env, company.id, codeid2tag)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    _migrate(env)


_migrate(env)
