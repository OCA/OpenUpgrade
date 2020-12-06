# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from uuid import uuid4

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
    savepoint = str(uuid4)
    try:
        self.env.cr.execute(  # pylint: disable=sql-injection
            'SAVEPOINT "%s"' % savepoint
        )
        return BaseModel.unlink._original_method(self)
    except Exception as e:
        self.env.cr.execute(  # pylint: disable=sql-injection
            'ROLLBACK TO SAVEPOINT "%s"' % savepoint
        )
        _logger.warning(
            "Could not delete obsolete record with ids %s of model %s: %s",
            self.ids,
            self._name,
            e,
        )
    return False


unlink._original_method = BaseModel.unlink
BaseModel.unlink = unlink
