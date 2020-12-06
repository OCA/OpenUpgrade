# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo import api, models
from odoo.tools import mute_logger

from odoo.addons.base.models.ir_model import IrModel, IrModelData, IrModelRelation


def _drop_table(self):
    """ Never drop tables """
    for model in self:
        if self.env.get(model.model) is not None:
            openupgrade.message(
                self.env.cr,
                "Unknown",
                False,
                False,
                "Not dropping the table or view of model %s",
                model.model,
            )


def _drop_column(self):
    """ Never drop columns """
    for field in self:
        if field.name in models.MAGIC_COLUMNS:
            continue
        openupgrade.message(
            self.env.cr,
            "Unknown",
            False,
            False,
            "Not dropping the column of field %s of model %s",
            field.name,
            field.model,
        )
        continue


IrModel._drop_column = _drop_column
IrModel._drop_table = _drop_table


@api.model
def _process_end(self, modules):
    """Don't warn about upgrade conventions from Odoo
    ('fields should be explicitely removed by an upgrade script')
    """
    with mute_logger("odoo.addons.base.models.ir_model"):
        return IrModelData._process_end._original_method(self, modules)


_process_end._original_method = IrModelData._process_end
IrModelData._process_end = _process_end


def _module_data_uninstall(self):
    """Don't delete many2many relation tables. Only unlink the
    ir.model.relation record itself.
    """
    self.unlink()


IrModelRelation._module_data_uninstall = _module_data_uninstall
