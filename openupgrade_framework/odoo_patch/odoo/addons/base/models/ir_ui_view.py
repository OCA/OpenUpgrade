# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api
from odoo.tools import mute_logger

from odoo.addons.base.models.ir_ui_view import View

_logger = logging.getLogger(__name__)


@api.constrains("arch_db")
def _check_xml(self):
    """ Mute warnings about views which are common during migration """
    with mute_logger("odoo.addons.base.models.ir_ui_view"):
        return View._check_xml._original_method(self)


def handle_view_error(
    self, message, *args, raise_exception=True, from_exception=None, from_traceback=None
):
    """Don't raise or log exceptions in view validation unless explicitely
    requested
    """
    raise_exception = self.env.context.get("raise_view_error")
    to_mute = "odoo.addons.base.models.ir_ui_view" if raise_exception else "not_muted"
    with mute_logger(to_mute):
        try:
            return View.handle_view_error._original_method(
                self,
                message,
                *args,
                raise_exception=False,
                from_exception=from_exception,
                from_traceback=from_traceback
            )
        except ValueError:
            _logger.warn(
                "Can't render custom view %s for model %s. "
                "Assuming you are migrating between major versions of "
                "Odoo, this view is now set to inactive. Please "
                "review the view contents manually after the migration.",
                self.xml_id,
                self.model,
            )
            self.write({"active": False})


_check_xml._original_method = View._check_xml
View._check_xml = _check_xml
handle_view_error._original_method = View.handle_view_error
View.handle_view_error = handle_view_error
