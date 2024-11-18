import logging
import os

from odoo.modules import get_module_path
from odoo.tools import config

from . import odoo_patch

if not config.get("upgrade_path"):
    path = get_module_path("openupgrade_scripts", display_warning=False)
    if path:
        logging.getLogger(__name__).info(
            "Setting upgrade_path to the scripts directory inside the module "
            "location of openupgrade_scripts"
        )
        config["upgrade_path"] = os.path.join(path, "scripts")


def openupgrade_test(cls):
    """
    Set attributes on a test class necessary for the test framework
    Use as decorator on test classes in openupgrade_scripts/scripts/*/tests/test_*.py
    """
    tags = getattr(cls, "test_tags", None) or set()
    if "openupgrade" not in tags:
        tags.add("openupgrade")
    if not any(t.endswith("_install") for t in tags):
        tags.add("at_install")
    cls.test_tags = tags
    cls.test_module = cls.__module__.split(".")[2]
    cls.test_class = cls.__name__
    cls.test_sequence = 0
    return cls
