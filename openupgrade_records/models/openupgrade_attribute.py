# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OpenupgradeAttribute(models.Model):
    _name = "openupgrade.attribute"
    _description = "OpenUpgrade Attribute"

    name = fields.Char(readonly=True)
    value = fields.Char(readonly=True)
    record_id = fields.Many2one(
        "openupgrade.record",
        ondelete="CASCADE",
        readonly=True,
    )
