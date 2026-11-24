# Copyright 2026 Sergio Corato <sergiocorato@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ast
import logging

from lxml import etree
from openupgradelib import openupgrade

from odoo.osv.expression import AND

_logger = logging.getLogger(__name__)


def _literal_eval(value):
    try:
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return None


def _convert_comparison(comparison, action_domain):
    """Convert a 14.0 dashboard comparison to the 16.0 format.

    The user saved the comparison of a dashboard action as the 14.0
    ``timeRanges`` object (``range``/``comparisonRange`` domains with their
    descriptions).  The 16.0 client only understands
    ``{fieldName, domains: [{arrayRepr, description}]}`` and drops anything
    else, see ``board_action.js``.  The dashboard domain is merged in each
    domain because the client uses the comparison as is.
    """
    if not isinstance(comparison, dict) or "domains" in comparison:
        return None
    field_name = comparison.get("fieldName")
    ranges = [
        (comparison.get("range"), comparison.get("rangeDescription")),
        (
            comparison.get("comparisonRange"),
            comparison.get("comparisonRangeDescription"),
        ),
    ]
    if not field_name or not all(raw for raw, _description in ranges):
        return None
    domains = []
    for raw, description in ranges:
        domain = _literal_eval(raw) if isinstance(raw, str) else raw
        if not isinstance(domain, list):
            return None
        domains.append(
            {
                "arrayRepr": AND([action_domain or [], domain]),
                "description": description,
            }
        )
    return {"fieldName": field_name, "domains": domains}


def _convert_dashboard(arch):
    """Convert the comparisons of an ``ir.ui.view.custom`` dashboard arch.

    Return the new arch, or None when there is nothing to convert.
    """
    try:
        root = etree.fromstring(arch)
    except etree.XMLSyntaxError:
        _logger.warning("Dashboard customization is not valid XML, skipped")
        return None
    changed = False
    for action in root.iter("action"):
        raw_context = action.get("context")
        if not raw_context or "comparison" not in raw_context:
            continue
        context = _literal_eval(raw_context)
        action_domain = _literal_eval(action.get("domain") or "[]")
        if not isinstance(context, dict) or not isinstance(action_domain, list):
            _logger.warning(
                "Dashboard action %s has an unexpected context or domain, skipped",
                action.get("name"),
            )
            continue
        comparison = _convert_comparison(context.get("comparison"), action_domain)
        if not comparison:
            continue
        context["comparison"] = comparison
        action.set("context", repr(context))
        changed = True
    if not changed:
        return None
    return etree.tostring(root, encoding="unicode")


@openupgrade.migrate()
def migrate(env, version):
    for custom_view in env["ir.ui.view.custom"].search([]):
        arch = _convert_dashboard(custom_view.arch)
        if arch:
            custom_view.arch = arch
