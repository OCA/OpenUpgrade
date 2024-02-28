# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo.api import Environment

_logger = logging.getLogger(__name__)


class FakeRecord:
    """Artificial construct to handle delete(records) submethod"""

    def __new__(cls):
        return object.__new__(cls)

    def __init__(self):
        self._name = "ir.model.data"
        self.ids = []
        self.browse = lambda x: None

    def __isub__(self, other):
        return None


def __getitem__(self, model_name):
    """This is used to bypass the call self.env[model]
    (and other posterior calls) from _module_data_uninstall method of ir.model.data
    """
    if (
        hasattr(self, "context")
        and isinstance(model_name, str)
        and self.context.get("missing_model", False)
    ):
        if not self.registry.models.get(model_name, False):
            new_env = lambda: None  # noqa: E731
            new_env._fields = {}
            new_env.browse = lambda i: FakeRecord()
            return new_env
    return Environment.__getitem__._original_method(self, model_name)


__getitem__._original_method = Environment.__getitem__
Environment.__getitem__ = __getitem__
