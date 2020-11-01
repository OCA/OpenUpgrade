# flake8: noqa
# pylint: skip-file

import logging
import odoo
import odoo.tools as tools
from odoo.tools.safe_eval import safe_eval

from odoo.modules.graph import Graph

_logger = logging.getLogger(__name__)


if True:

    def _update_from_db(self, cr):
        if not len(self):
            return
        # update the graph with values from the database (if exist)
        ## First, we set the default values for each package in graph
        additional_data = {key: {'id': 0, 'state': 'uninstalled', 'dbdemo': False, 'installed_version': None} for key in self.keys()}
        ## Then we get the values from the database
        cr.execute('SELECT name, id, state, demo AS dbdemo, latest_version AS installed_version'
                   '  FROM ir_module_module'
                   ' WHERE name IN %s',(tuple(additional_data),)
                   )

        ## and we update the default values with values from the database
        additional_data.update((x['name'], x) for x in cr.dictfetchall())

        # <OpenUpgrade:ADD>
        # Prevent reloading of demo data from the new version on major upgrade
        if ('base' in self and additional_data['base']['dbdemo'] and
                additional_data['base']['installed_version'] <
                odoo.release.major_version):
            cr.execute("UPDATE ir_module_module SET demo = false")
            for data in additional_data.values():
                data['dbdemo'] = False
        # </OpenUpgrade>

        for package in self.values():
            for k, v in additional_data[package.name].items():
                setattr(package, k, v)


    def _add_modules(self, cr, module_list, force=None):
        if force is None:
            force = []
        packages = []
        len_graph = len(self)

        # <OpenUpgrade:ADD>
        # force additional dependencies for the upgrade process if given
        # in config file
        forced_deps = tools.config.get_misc('openupgrade', 'force_deps', '{}')
        forced_deps = tools.config.get_misc('openupgrade',
                                            'force_deps_' + odoo.release.version,
                                            forced_deps)
        forced_deps = safe_eval(forced_deps)
        # </OpenUpgrade>

        for module in module_list:
            # This will raise an exception if no/unreadable descriptor file.
            # NOTE The call to load_information_from_description_file is already
            # done by db.initialize, so it is possible to not do it again here.
            info = odoo.modules.module.load_information_from_description_file(module)
            if info and info['installable']:
                # <OpenUpgrade:ADD>
                info['depends'].extend(forced_deps.get(module, []))
                # </OpenUpgrade>
                packages.append((module, info)) # TODO directly a dict, like in get_modules_with_version
            elif module != 'studio_customization':
                _logger.warning('module %s: not installable, skipped', module)

        dependencies = dict([(p, info['depends']) for p, info in packages])
        current, later = set([p for p, info in packages]), set()

        while packages and current > later:
            package, info = packages[0]
            deps = info['depends']

            # if all dependencies of 'package' are already in the graph, add 'package' in the graph
            if all(dep in self for dep in deps):
                if not package in current:
                    packages.pop(0)
                    continue
                later.clear()
                current.remove(package)
                node = self.add_node(package, info)
                for kind in ('init', 'demo', 'update'):
                    if package in tools.config[kind] or 'all' in tools.config[kind] or kind in force:
                        setattr(node, kind, True)
            else:
                later.add(package)
                packages.append((package, info))
            packages.pop(0)

        self.update_from_db(cr)

        for package in later:
            unmet_deps = [p for p in dependencies[package] if p not in self]
            _logger.info('module %s: Unmet dependencies: %s', package, ', '.join(unmet_deps))

        return len(self) - len_graph


Graph.update_from_db = _update_from_db
Graph.add_modules = _add_modules
