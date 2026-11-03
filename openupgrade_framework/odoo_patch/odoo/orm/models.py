# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo.models import BaseModel

from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG

_logger = logging.getLogger(__name__)


def unlink(self):
    """Don't break on unlink of obsolete records
    when called from ir.model::_process_end()

    This only adapts the base unlink method. If overrides of this method
    on individual models give problems, add patches for those as well.
    """
    if not self.env.context.get(MODULE_UNINSTALL_FLAG):
        return BaseModel.unlink._original_method(self)
    try:
        with self.env.cr.savepoint():
            return BaseModel.unlink._original_method(self)
    except Exception as e:
        _logger.warning(
            "Could not delete obsolete record with ids %s of model %s",
            self.ids,
            self._name,
            exc_info=e,
        )
    return False


unlink._original_method = BaseModel.unlink
BaseModel.unlink = unlink
