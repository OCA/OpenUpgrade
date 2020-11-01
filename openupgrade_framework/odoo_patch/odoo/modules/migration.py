# flake8: noqa
# pylint: skip-file

import logging
import os
from os.path import join as opj
import odoo.release as release
from odoo.tools.parse_version import parse_version

import odoo
from odoo.modules.migration import load_script
from odoo.modules import migration

_logger = logging.getLogger(__name__)


if True:
    def _migrate_module(self, pkg, stage):
        assert stage in ('pre', 'post', 'end')
        stageformat = {
            'pre': '[>%s]',
            'post': '[%s>]',
            'end': '[$%s]',
        }
        state = pkg.state if stage in ('pre', 'post') else getattr(pkg, 'load_state', None)

        # <OpenUpgrade:CHANGE>
        # In openupgrade, also run migration scripts upon installation.
        # We want to always pass in pre and post migration files and use a new
        # argument in the migrate decorator (explained in the docstring)
        # to decide if we want to do something if a new module is installed
        # during the migration.
        if not (hasattr(pkg, 'update') or state in ('to upgrade', 'to install')):
        # </OpenUpgrade>
            return

        def convert_version(version):
            if version.count('.') >= 2:
                return version  # the version number already containt the server version
            return "%s.%s" % (release.major_version, version)

        def _get_migration_versions(pkg, stage):
            versions = sorted({
                ver
                for lv in self.migrations[pkg.name].values()
                for ver, lf in lv.items()
                if lf
            }, key=lambda k: parse_version(convert_version(k)))
            if "0.0.0" in versions:
                # reorder versions
                versions.remove("0.0.0")
                if stage == "pre":
                    versions.insert(0, "0.0.0")
                else:
                    versions.append("0.0.0")
            return versions

        def _get_migration_files(pkg, version, stage):
            """ return a list of migration script files
            """
            m = self.migrations[pkg.name]
            lst = []

            mapping = {
                'module': opj(pkg.name, 'migrations'),
                'module_upgrades': opj(pkg.name, 'upgrades'),
            }

            for path in odoo.upgrade.__path__:
                if os.path.exists(opj(path, pkg.name)):
                    mapping['upgrade'] = opj(path, pkg.name)
                    break

            for x in mapping:
                if version in m.get(x):
                    for f in m[x][version]:
                        if not f.startswith(stage + '-'):
                            continue
                        lst.append(opj(mapping[x], version, f))
            lst.sort()
            return lst

        installed_version = getattr(pkg, 'load_version', pkg.installed_version) or ''
        parsed_installed_version = parse_version(installed_version)
        current_version = parse_version(convert_version(pkg.data['version']))

        versions = _get_migration_versions(pkg, stage)

        for version in versions:
            if ((version == "0.0.0" and parsed_installed_version < current_version)
               or parsed_installed_version < parse_version(convert_version(version)) <= current_version):

                strfmt = {'addon': pkg.name,
                          'stage': stage,
                          'version': stageformat[stage] % version,
                          }

                for pyfile in _get_migration_files(pkg, version, stage):
                    name, ext = os.path.splitext(os.path.basename(pyfile))
                    if ext.lower() != '.py':
                        continue
                    mod = None
                    try:
                        mod = load_script(pyfile, name)
                        _logger.info('module %(addon)s: Running migration %(version)s %(name)s' % dict(strfmt, name=mod.__name__))
                        migrate = mod.migrate
                    except ImportError:
                        _logger.exception('module %(addon)s: Unable to load %(stage)s-migration file %(file)s' % dict(strfmt, file=pyfile))
                        raise
                    except AttributeError:
                        _logger.error('module %(addon)s: Each %(stage)s-migration file must have a "migrate(cr, installed_version)" function' % strfmt)
                    else:
                        migrate(self.cr, installed_version)
                    finally:
                        if mod:
                            del mod

migration.migrate_module = _migrate_module
