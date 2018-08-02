# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

""" Modules migration handling. """

from collections import defaultdict
import glob
import imp
import logging
import os
from os.path import join as opj

from openerp.modules.module import get_resource_path
import openerp.release as release
import openerp.tools as tools
from openerp.tools.parse_version import parse_version


_logger = logging.getLogger(__name__)

class MigrationManager(object):
    """
        This class manage the migration of modules
        Migrations files must be python files containing a `migrate(cr, installed_version)`
        function. Theses files must respect a directory tree structure: A 'migrations' folder
        which containt a folder by version. Version can be 'module' version or 'server.module'
        version (in this case, the files will only be processed by this version of the server).
        Python file names must start by `pre` or `post` and will be executed, respectively,
        before and after the module initialisation. `end` scripts are run after all modules have
        been updated.

        Example:

            <moduledir>
            `-- migrations
                |-- 1.0
                |   |-- pre-update_table_x.py
                |   |-- pre-update_table_y.py
                |   |-- post-create_plop_records.py
                |   |-- end-cleanup.py
                |   `-- README.txt                      # not processed
                |-- 9.0.1.1                             # processed only on a 9.0 server
                |   |-- pre-delete_table_z.py
                |   `-- post-clean-data.py
                `-- foo.py                              # not processed

    """

    def __init__(self, cr, graph):
        self.cr = cr
        self.graph = graph
        self.migrations = defaultdict(dict)
        self._get_files()

    def _get_files(self):
        def get_scripts(path):
            if not path:
                return {}
            return {
                version: glob.glob1(opj(path, version), '*.py')
                for version in os.listdir(path)
                if os.path.isdir(opj(path, version))
            }

        for pkg in self.graph:
            if not (hasattr(pkg, 'update') or pkg.state == 'to upgrade' or
                    getattr(pkg, 'load_state', None) == 'to upgrade'):
                continue

            self.migrations[pkg.name] = {
                'module': get_scripts(get_resource_path(pkg.name, 'migrations')),
                'maintenance': get_scripts(get_resource_path('base', 'maintenance', 'migrations', pkg.name)),
            }

    def migrate_module(self, pkg, stage):
        assert stage in ('pre', 'post', 'end')
        stageformat = {
            'pre': '[>%s]',
            'post': '[%s>]',
            'end': '[$%s]',
        }
        state = pkg.state if stage in ('pre', 'post') else getattr(pkg, 'load_state', None)

        # In openupgrade, remove 'or pkg.installed_version is None'
        # We want to always pass in pre and post migration files and use a new
        # argument in the migrate decorator (explained in the docstring)
        # to decide if we want to do something if a new module is installed
        # during the migration.

        if not (hasattr(pkg, 'update') or state == 'to upgrade'):
            return

        def convert_version(version):
            if version.count('.') >= 2:
                return version  # the version number already containt the server version
            return "%s.%s" % (release.major_version, version)

        def _get_migration_versions(pkg):
            versions = list(set(
                ver
                for lv in self.migrations[pkg.name].values()
                for ver, lf in lv.items()
                if lf
            ))
            versions.sort(key=lambda k: parse_version(convert_version(k)))
            return versions

        def _get_migration_files(pkg, version, stage):
            """ return a list of migration script files
            """
            m = self.migrations[pkg.name]
            lst = []

            mapping = {
                'module': opj(pkg.name, 'migrations'),
                'maintenance': opj('base', 'maintenance', 'migrations', pkg.name),
            }

            for x in mapping.keys():
                if version in m.get(x):
                    for f in m[x][version]:
                        if not f.startswith(stage + '-'):
                            continue
                        lst.append(opj(mapping[x], version, f))
            lst.sort()
            return lst

        def mergedict(a, b):
            a = a.copy()
            a.update(b)
            return a

        installed_version = getattr(pkg, 'load_version', pkg.installed_version) or ''
        parsed_installed_version = parse_version(installed_version)
        current_version = parse_version(convert_version(pkg.data['version']))

        versions = _get_migration_versions(pkg)

        for version in versions:
            if parsed_installed_version < parse_version(convert_version(version)) <= current_version:

                strfmt = {'addon': pkg.name,
                          'stage': stage,
                          'version': stageformat[stage] % version,
                          }

                for pyfile in _get_migration_files(pkg, version, stage):
                    name, ext = os.path.splitext(os.path.basename(pyfile))
                    if ext.lower() != '.py':
                        continue
                    # OpenUpgrade edit start:
                    # Removed a copy of migration script to temp directory
                    # Replaced call to load_source with load_module so frame isn't lost and breakpoints can be set
                    mod = fp = None
                    try:
                        fp, pathname = tools.file_open(pyfile, pathinfo=True)
                        try:
                            mod = imp.load_module(name, fp, pathname, ('.py', 'r', imp.PY_SOURCE))
                            _logger.info('module %(addon)s: Running migration %(version)s %(name)s',
                                         mergedict({'name': mod.__name__}, strfmt))
                        except ImportError:
                            _logger.exception('module %(addon)s: Unable to load %(stage)s-migration file %(file)s',
                                              mergedict({'file': pyfile}, strfmt))
                            raise

                        _logger.info('module %(addon)s: Running migration %(version)s %(name)s',
                                     mergedict({'name': mod.__name__}, strfmt))

                        if hasattr(mod, 'migrate'):
                            mod.migrate(self.cr, installed_version)
                        else:
                            _logger.error('module %(addon)s: Each %(stage)s-migration file must have a "migrate(cr, installed_version)" function',
                                          strfmt)
                    finally:
                        if fp:
                            fp.close()
                        if mod:
                            del mod
                    # OpenUpgrade edit end
