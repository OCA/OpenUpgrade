# flake8: noqa
# pylint: skip-file

import logging
import os
import time

import odoo
from odoo.tools import config
from odoo.modules.registry import Registry

from odoo.service import server
from odoo.service.server import load_test_file_py

_logger = logging.getLogger(__name__)


def preload_registries(dbnames):
    """ Preload a registries, possibly run a test file."""
    # TODO: move all config checks to args dont check tools.config here
    dbnames = dbnames or []
    rc = 0
    for dbname in dbnames:
        try:
            update_module = config['init'] or config['update']
            registry = Registry.new(dbname, update_module=update_module)

            # run test_file if provided
            if config['test_file']:
                test_file = config['test_file']
                if not os.path.isfile(test_file):
                    _logger.warning('test file %s cannot be found', test_file)
                elif not test_file.endswith('py'):
                    _logger.warning('test file %s is not a python file', test_file)
                else:
                    _logger.info('loading test file %s', test_file)
                    with odoo.api.Environment.manage():
                        load_test_file_py(registry, test_file)

            # run post-install tests
            if config['test_enable']:
                t0 = time.time()
                t0_sql = odoo.sql_db.sql_counter
                module_names = (registry.updated_modules if update_module else
                                sorted(registry._init_modules))
                _logger.info("Starting post tests")
                tests_before = registry._assertion_report.testsRun
                with odoo.api.Environment.manage():
                    for module_name in module_names:
                        result = loader.run_suite(loader.make_suite(module_name, 'post_install'), module_name)
                        registry._assertion_report.update(result)
                    # <OpenUpgrade:ADD>
                    # run deferred unit tests
                    for module_name, prefix in registry.openupgrade_test_prefixes:
                        result = run_unit_tests(module_name, position='post_install', openupgrade_prefix=prefix)
                        registry._assertion_report.record_result(result)
                    # </OpenUpgrade>
                _logger.info("%d post-tests in %.2fs, %s queries",
                             registry._assertion_report.testsRun - tests_before,
                             time.time() - t0,
                             odoo.sql_db.sql_counter - t0_sql)

            if not registry._assertion_report.wasSuccessful():
                rc += 1
        except Exception:
            _logger.critical('Failed to initialize database `%s`.', dbname, exc_info=True)
            return -1
    return rc


server.preload_registries = preload_registries
