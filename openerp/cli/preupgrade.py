#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 Daniel Reis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import glob
import os

import openerp
from openerp.api import Environment
from openerp.release import major_version
from . import Command


class PreUpgrade(Command):
    """OpenUpgrade module precheck"""

    def init(self, args):
        openerp.tools.config.parse_config(args)
        openerp.cli.server.report_configuration()
        openerp.service.server.start(preload=[], stop=True)

    def get_ignore_list(self):
        addons_list = openerp.tools.config['addons_path'].split(',')
        to_ignore = list()
        for addons in addons_list:
            for ignore in glob.glob(os.path.join(addons, '*.migrate')):
                lines = open(os.path.join(addons, ignore)).readlines()
                to_ignore.extend(lines)
        return {x.split(',')[0].strip(): ',' in x and x.split(',')[1].strip()
                for x in to_ignore}

    def get_module_dir(self, module):
        addons_list = openerp.tools.config['addons_path'].split(',')
        paths = [os.path.join(x, module.name)
                 for x in addons_list
                 if os.path.isdir(os.path.join(x, module.name))]
        return paths and paths[0]

    def has_module_dir(self, module):
        path_dir = self.get_module_dir(module)
        return path_dir and os.path.isdir(path_dir)

    def get_module_migdir(self, module):
        path = self.get_module_dir(module)
        if path:
            version = module.installed_version
            if len(version.split('.')) <= 2:
                version = '%s.%s' % (major_version, version)
            path_mig = os.path.join(path, 'migrations', version)
            return os.path.isdir(path_mig) and path_mig

    def has_migration_scripts(self, module):
        path_mig = self.get_module_migdir(module)
        return path_mig and bool(glob.glob(os.path.join(path_mig, '*.py')))

    def run_preupgrade(self, env):
        Modules = env['ir.module.module']
        modules = Modules.search(
            [('state',
              'in',
              ['installed', 'to_install', 'to_upgrade'])],
            order='name')
        ignore = self.get_ignore_list()
        result = {'ready': [], 'missing': [], 'not ready': []}
        for module in modules:
            name_orig = module.name
            name_new = ignore.get(module.name) or module.name
            if name_orig in ignore and name_orig == name_new:
                result['ready'].append(name_orig)
            elif not self.has_module_dir(module):
                result['missing'].append(name_new)
            elif not self.has_migration_scripts(module):
                result['not ready'].append(name_new)
            else:
                result['ready'].append(name_new)
        return result

    def run(self, cmdargs):
        self.init(cmdargs)
        dbname = openerp.tools.config['db_name']
        with Environment.manage():
            registry = openerp.modules.registry.RegistryManager.get(dbname)
            with registry.cursor() as cr:
                uid = openerp.SUPERUSER_ID
                ctx = Environment(cr, uid, {})['res.users'].context_get()
                env = Environment(cr, uid, ctx)
                result = self.run_preupgrade(env)
                for title in result:
                    print '\n', title, '\n', '='*10
                    for x in result[title]:
                        print x
