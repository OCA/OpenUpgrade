# flake8: noqa
# pylint: skip-file

# from odoo.addons.openupgrade_framework.openupgrade import openupgrade_log

from odoo.tools import view_validation
from odoo.tools.view_validation import _validators, _logger


def _valid_view(arch, **kwargs):
    for pred in _validators[arch.tag]:
        # <OpenUpgrade:CHANGE>
        # Do not raise blocking error, because it's normal to
        # have inconsistent views in an openupgrade process
        check = pred(arch, **kwargs) or 'Warning'
        # </OpenUpgrade>
        if not check:
            _logger.error("Invalid XML: %s", pred.__doc__)
            return False
        if check == "Warning":
            # <OpenUpgrade:REM>
            # Don't show this warning as useless and too much verbose
            # _logger.warning("Invalid XML: %s", pred.__doc__)
            # </OpenUpgrade>
            return "Warning"
    return True


view_validation.valid_view = _valid_view
