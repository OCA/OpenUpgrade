# Copyright 2023 Hunki Enterprises BV (https://hunki-enterprises.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import importlib
import inspect
import os.path
import sys

from odoo.tests import loader
from odoo.tools import config


def _get_tests_modules(mod):
    """
    Make odoo load tests from openupgrade_scripts/scripts/$module/$version/tests
    instead of the standard location
    """
    # <OpenUpgrade:ADD>
    package = None
    frame = inspect.currentframe().f_back
    while frame and not package:
        package = frame.f_locals.get("package")
        frame = frame.f_back

    if not package:
        return []

    spec = importlib.util.spec_from_file_location(
        "%s_migration_tests" % mod.name,
        os.path.join(
            config["upgrade_path"],
            package.name,
            package.data["version"] or ".",
            "tests",
            "__init__.py",
        ),
    )

    if not spec:
        return []

    test_module = importlib.util.module_from_spec(spec)
    sys.modules[test_module.__name__] = test_module

    try:
        spec.loader.exec_module(test_module)
    except FileNotFoundError:
        del sys.modules[test_module.__name__]
        return []
    # </OpenUpgrade>
    tests_mod = importlib.import_module(spec.name)
    return [
        mod_obj
        for name, mod_obj in inspect.getmembers(tests_mod, inspect.ismodule)
        if name.startswith("test_")
    ]


_get_tests_modules._original_method = loader._get_tests_modules
loader._get_tests_modules = _get_tests_modules
