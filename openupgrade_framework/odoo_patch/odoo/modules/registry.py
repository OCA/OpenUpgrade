# flake8: noqa
# pylint: skip-file

from collections import deque
from contextlib import closing
import odoo
from odoo.tools.lru import LRU

from odoo.modules import registry


if True:

    def _init(self, db_name):
        self.models = {}    # model name/model instance mapping
        self._sql_constraints = set()
        self._init = True
        self._assertion_report = odoo.tests.runner.OdooTestResult()
        self._fields_by_model = None
        self._ordinary_tables = None
        self._constraint_queue = deque()
        self.__cache = LRU(8192)

        # modules fully loaded (maintained during init phase by `loading` module)
        self._init_modules = set()
        self.updated_modules = []       # installed/updated modules
        # <OpenUpgrade:ADD>
        self.openupgrade_test_prefixes = {}
        # </OpenUpgrade>
        self.loaded_xmlids = set()

        self.db_name = db_name
        self._db = odoo.sql_db.db_connect(db_name)

        # cursor for test mode; None means "normal" mode
        self.test_cr = None
        self.test_lock = None

        # Indicates that the registry is
        self.loaded = False             # whether all modules are loaded
        self.ready = False              # whether everything is set up

        # Inter-process signaling:
        # The `base_registry_signaling` sequence indicates the whole registry
        # must be reloaded.
        # The `base_cache_signaling sequence` indicates all caches must be
        # invalidated (i.e. cleared).
        self.registry_sequence = None
        self.cache_sequence = None

        # Flags indicating invalidation of the registry or the cache.
        self.registry_invalidated = False
        self.cache_invalidated = False

        with closing(self.cursor()) as cr:
            self.has_unaccent = odoo.modules.db.has_unaccent(cr)

registry.init = _init
