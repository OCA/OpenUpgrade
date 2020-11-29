# flake8: noqa
# pylint: skip-file

import itertools
import logging
import sys
import time

import odoo
import odoo.tools as tools
from odoo import api, SUPERUSER_ID
from odoo.modules import loading
from odoo.modules.module import adapt_version, load_openerp_module, initialize_sys_path

from odoo.modules.loading import load_data, load_demo, _check_module_names
from odoo.addons.openupgrade_framework.openupgrade import openupgrade_loading

import os

_logger = logging.getLogger(__name__)
_test_logger = logging.getLogger('odoo.tests')


def _load_module_graph(cr, graph, status=None, perform_checks=True,
                      skip_modules=None, report=None, models_to_check=None):
    """Migrates+Updates or Installs all module nodes from ``graph``
       :param graph: graph of module nodes to load
       :param status: deprecated parameter, unused, left to avoid changing signature in 8.0
       :param perform_checks: whether module descriptors should be checked for validity (prints warnings
                              for same cases)
       :param skip_modules: optional list of module names (packages) which have previously been loaded and can be skipped
       :return: list of modules that were installed or updated
    """
    if skip_modules is None:
        skip_modules = []

    if models_to_check is None:
        models_to_check = set()

    processed_modules = []
    loaded_modules = []
    registry = odoo.registry(cr.dbname)
    migrations = odoo.modules.migration.MigrationManager(cr, graph)
    module_count = len(graph)
    _logger.info('loading %d modules...', module_count)

    # <OpenUpgrade:ADD>
    # suppress commits to have the upgrade of one module in just one transaction
    cr.commit_org = cr.commit
    cr.commit = lambda *args: None
    cr.rollback_org = cr.rollback
    cr.rollback = lambda *args: None
    # </OpenUpgrade>

    # register, instantiate and initialize models for each modules
    t0 = time.time()
    loading_extra_query_count = odoo.sql_db.sql_counter
    loading_cursor_query_count = cr.sql_log_count

    models_updated = set()

    for index, package in enumerate(graph, 1):
        module_name = package.name
        module_id = package.id

        # <OpenUpgrade:CHANGE>
        if module_name in skip_modules or module_name in loaded_modules:
            # </OpenUpgrade>
            continue

        module_t0 = time.time()
        module_cursor_query_count = cr.sql_log_count
        module_extra_query_count = odoo.sql_db.sql_counter

        needs_update = (
            hasattr(package, "init")
            or hasattr(package, "update")
            or package.state in ("to install", "to upgrade")
        )
        module_log_level = logging.DEBUG
        if needs_update:
            module_log_level = logging.INFO
        _logger.log(module_log_level, 'Loading module %s (%d/%d)', module_name, index, module_count)

        if needs_update:
            if package.name != 'base':
                registry.setup_models(cr)
            migrations.migrate_module(package, 'pre')
            if package.name != 'base':
                env = api.Environment(cr, SUPERUSER_ID, {})
                env['base'].flush()

        load_openerp_module(package.name)

        new_install = package.state == 'to install'
        if new_install:
            py_module = sys.modules['odoo.addons.%s' % (module_name,)]
            pre_init = package.info.get('pre_init_hook')
            if pre_init:
                getattr(py_module, pre_init)(cr)

        model_names = registry.load(cr, package)

        mode = 'update'
        if hasattr(package, 'init') or package.state == 'to install':
            mode = 'init'

        loaded_modules.append(package.name)
        if needs_update:
            models_updated |= set(model_names)
            models_to_check -= set(model_names)
            registry.setup_models(cr)

            registry.init_models(cr, model_names, {'module': package.name}, new_install)
        elif package.state != 'to remove':
            # The current module has simply been loaded. The models extended by this module
            # and for which we updated the schema, must have their schema checked again.
            # This is because the extension may have changed the model,
            # e.g. adding required=True to an existing field, but the schema has not been
            # updated by this module because it's not marked as 'to upgrade/to install'.
            models_to_check |= set(model_names) & models_updated

        idref = {}

        if needs_update:
            env = api.Environment(cr, SUPERUSER_ID, {})
            # Can't put this line out of the loop: ir.module.module will be
            # registered by init_models() above.
            module = env['ir.module.module'].browse(module_id)

            if perform_checks:
                module._check()

            if package.state == 'to upgrade':
                # upgrading the module information
                module.write(module.get_values_from_terp(package.data))
            load_data(cr, idref, mode, kind='data', package=package)
            demo_loaded = package.dbdemo = load_demo(cr, package, idref, mode)
            cr.execute('update ir_module_module set demo=%s where id=%s', (demo_loaded, module_id))
            module.invalidate_cache(['demo'])

            # <OpenUpgrade:CHANGE>
            # add 'try' block for logging exceptions
            # as errors in post scripts seem to be dropped
            try:
                migrations.migrate_module(package, 'post')
            except Exception as exc:
                _logger.error('Error executing post migration script for module %s: %s',
                              package, exc)
                raise
            # </OpenUpgrade>

            # Update translations for all installed languages
            overwrite = odoo.tools.config["overwrite_existing_translations"]
            module.with_context(overwrite=overwrite)._update_translations()

        if package.name is not None:
            registry._init_modules.add(package.name)

        if needs_update:
            if new_install:
                post_init = package.info.get('post_init_hook')
                if post_init:
                    getattr(py_module, post_init)(cr, registry)

            if mode == 'update':
                # validate the views that have not been checked yet
                env['ir.ui.view']._validate_module_views(module_name)

            # need to commit any modification the module's installation or
            # update made to the schema or data so the tests can run
            # (separately in their own transaction)
            # <OpenUpgrade:CHANGE>
            # commit after processing every module as well, for
            # easier debugging and continuing an interrupted migration
            cr.commit_org()
            # </OpenUpgrade

        updating = tools.config.options['init'] or tools.config.options['update']
        test_time = test_queries = 0
        test_results = None
        if tools.config.options['test_enable'] and (needs_update or not updating):
            env = api.Environment(cr, SUPERUSER_ID, {})
            loader = odoo.tests.loader
            suite = loader.make_suite(module_name, 'at_install')
            if suite.countTestCases():
                if not needs_update:
                    registry.setup_models(cr)
                # Python tests
                env['ir.http']._clear_routing_map()     # force routing map to be rebuilt

                tests_t0, tests_q0 = time.time(), odoo.sql_db.sql_counter
                test_results = loader.run_suite(suite, module_name)
                report.update(test_results)
                test_time = time.time() - tests_t0
                test_queries = odoo.sql_db.sql_counter - tests_q0

                # tests may have reset the environment
                env = api.Environment(cr, SUPERUSER_ID, {})
                module = env['ir.module.module'].browse(module_id)

        if needs_update:
            # <OpenUpgrade:CHANGE>
            # run tests
            if os.environ.get('OPENUPGRADE_TESTS') and package.name is not None:
                prefix = '.migrations'
                registry.openupgrade_test_prefixes[package.name] = prefix
                report.record_result(odoo.modules.module.run_unit_tests(module_name, openupgrade_prefix=prefix))
            # </OpenUpgrade

            processed_modules.append(package.name)

            ver = adapt_version(package.data['version'])
            # Set new modules and dependencies
            module.write({'state': 'installed', 'latest_version': ver})
            # <OpenUpgrade:ADD>
            # commit module_n state and version immediatly
            # to avoid invalid database state if module_n+1 raises an
            # exception
            cr.commit_org()
            # </OpenUpgrade>

            package.load_state = package.state
            package.load_version = package.installed_version
            package.state = 'installed'
            for kind in ('init', 'demo', 'update'):
                if hasattr(package, kind):
                    delattr(package, kind)
            module.flush()

        extra_queries = odoo.sql_db.sql_counter - module_extra_query_count - test_queries
        extras = []
        if test_queries:
            extras.append(f'+{test_queries} test')
        if extra_queries:
            extras.append(f'+{extra_queries} other')
        _logger.log(
            module_log_level, "Module %s loaded in %.2fs%s, %s queries%s",
            module_name, time.time() - module_t0,
            f' (incl. {test_time:.2f}s test)' if test_time else '',
            cr.sql_log_count - module_cursor_query_count,
            f' ({", ".join(extras)})' if extras else ''
        )
        if test_results and not test_results.wasSuccessful():
            _logger.error(
                "Module %s: %d failures, %d errors of %d tests",
                module_name, len(test_results.failures), len(test_results.errors),
                test_results.testsRun
            )

    _logger.runbot("%s modules loaded in %.2fs, %s queries (+%s extra)",
                   len(graph),
                   time.time() - t0,
                   cr.sql_log_count - loading_cursor_query_count,
                   odoo.sql_db.sql_counter - loading_extra_query_count)  # extra queries: testes, notify, any other closed cursor

    # <OpenUpgrade:ADD>
    # restore commit method
    cr.commit = cr.commit_org
    cr.commit()
    # </OpenUpgrade>

    return loaded_modules, processed_modules


def _load_marked_modules(cr, graph, states, force, progressdict, report,
                        loaded_modules, perform_checks, models_to_check=None):
    """Loads modules marked with ``states``, adding them to ``graph`` and
       ``loaded_modules`` and returns a list of installed/upgraded modules."""

    if models_to_check is None:
        models_to_check = set()

    processed_modules = []
    while True:
        cr.execute("SELECT name from ir_module_module WHERE state IN %s" ,(tuple(states),))
        module_list = [name for (name,) in cr.fetchall() if name not in graph]
        # <OpenUpgrade:ADD>
        module_list = openupgrade_loading.add_module_dependencies(cr, module_list)
        # </OpenUpgrade>
        if not module_list:
            break
        graph.add_modules(cr, module_list, force)
        _logger.debug('Updating graph with %d more modules', len(module_list))
        loaded, processed = _load_module_graph(
            cr, graph, progressdict, report=report, skip_modules=loaded_modules,
            perform_checks=perform_checks, models_to_check=models_to_check,
        )
        processed_modules.extend(processed)
        loaded_modules.extend(loaded)
        if not processed:
            break
    return processed_modules


def _load_modules(db, force_demo=False, status=None, update_module=False):
    initialize_sys_path()

    force = []
    if force_demo:
        force.append('demo')

    models_to_check = set()

    with db.cursor() as cr:
        if not odoo.modules.db.is_initialized(cr):
            if not update_module:
                _logger.error("Database %s not initialized, you can force it with `-i base`", cr.dbname)
                return
            _logger.info("init db")
            odoo.modules.db.initialize(cr)
            update_module = True # process auto-installed modules
            tools.config["init"]["all"] = 1
            if not tools.config['without_demo']:
                tools.config["demo"]['all'] = 1

        # This is a brand new registry, just created in
        # odoo.modules.registry.Registry.new().
        registry = odoo.registry(cr.dbname)

        if 'base' in tools.config['update'] or 'all' in tools.config['update']:
            cr.execute("update ir_module_module set state=%s where name=%s and state=%s", ('to upgrade', 'base', 'installed'))

        # STEP 1: LOAD BASE (must be done before module dependencies can be computed for later steps)
        graph = odoo.modules.graph.Graph()
        graph.add_module(cr, 'base', force)
        if not graph:
            _logger.critical('module base cannot be loaded! (hint: verify addons-path)')
            raise ImportError('Module `base` cannot be loaded! (hint: verify addons-path)')

        # processed_modules: for cleanup step after install
        # loaded_modules: to avoid double loading
        report = registry._assertion_report
        loaded_modules, processed_modules = _load_module_graph(
            cr, graph, status, perform_checks=update_module,
            report=report, models_to_check=models_to_check)

        # </OpenUpgrade>
        load_lang = tools.config.pop('load_language')
        if load_lang or update_module:
            # some base models are used below, so make sure they are set up
            registry.setup_models(cr)

        if load_lang:
            for lang in load_lang.split(','):
                tools.load_language(cr, lang)

        # STEP 2: Mark other modules to be loaded/updated
        if update_module:
            env = api.Environment(cr, SUPERUSER_ID, {})
            Module = env['ir.module.module']
            _logger.info('updating modules list')
            Module.update_list()

            _check_module_names(cr, itertools.chain(tools.config['init'], tools.config['update']))

            module_names = [k for k, v in tools.config['init'].items() if v]
            if module_names:
                modules = Module.search([('state', '=', 'uninstalled'), ('name', 'in', module_names)])
                if modules:
                    modules.button_install()

            module_names = [k for k, v in tools.config['update'].items() if v]
            if module_names:
                # <OpenUpgrade:CHANGE>
                # in standard Odoo, '--update all' just means:
                # '--update base + upward (installed) dependencies. This breaks
                # the chain when new glue modules are encountered.
                # E.g. purchase in 8.0 depends on stock_account and report,
                # both of which are new. They may be installed, but purchase as
                # an upward dependency is not selected for upgrade.
                # Therefore, explicitely select all installed modules for
                # upgrading in OpenUpgrade in that case.
                domain = [('state', '=', 'installed')]
                if 'all' not in module_names:
                    domain.append(('name', 'in', module_names))
                modules = Module.search(domain)
                # </OpenUpgrade>
                if modules:
                    modules.button_upgrade()

            cr.execute("update ir_module_module set state=%s where name=%s", ('installed', 'base'))
            Module.invalidate_cache(['state'])
            Module.flush()

        # STEP 3: Load marked modules (skipping base which was done in STEP 1)
        # IMPORTANT: this is done in two parts, first loading all installed or
        #            partially installed modules (i.e. installed/to upgrade), to
        #            offer a consistent system to the second part: installing
        #            newly selected modules.
        #            We include the modules 'to remove' in the first step, because
        #            they are part of the "currently installed" modules. They will
        #            be dropped in STEP 6 later, before restarting the loading
        #            process.
        # IMPORTANT 2: We have to loop here until all relevant modules have been
        #              processed, because in some rare cases the dependencies have
        #              changed, and modules that depend on an uninstalled module
        #              will not be processed on the first pass.
        #              It's especially useful for migrations.
        previously_processed = -1
        while previously_processed < len(processed_modules):
            previously_processed = len(processed_modules)
            processed_modules += _load_marked_modules(cr, graph,
                ['installed', 'to upgrade', 'to remove'],
                force, status, report, loaded_modules, update_module, models_to_check)
            if update_module:
                processed_modules += _load_marked_modules(cr, graph,
                    ['to install'], force, status, report,
                    loaded_modules, update_module, models_to_check)
        # check that new module dependencies have been properly installed after a migration/upgrade
        cr.execute("SELECT name from ir_module_module WHERE state IN ('to install', 'to upgrade')")
        module_list = [name for (name,) in cr.fetchall()]
        if module_list:
            _logger.error("Some modules have inconsistent states, some dependencies may be missing: %s", sorted(module_list))

        # check that all installed modules have been loaded by the registry after a migration/upgrade
        cr.execute("SELECT name from ir_module_module WHERE state = 'installed' and name != 'studio_customization'")
        module_list = [name for (name,) in cr.fetchall() if name not in graph]
        if module_list:
            _logger.error("Some modules are not loaded, some dependencies or manifest may be missing: %s", sorted(module_list))

        registry.loaded = True
        registry.setup_models(cr)

        # STEP 3.5: execute migration end-scripts
        migrations = odoo.modules.migration.MigrationManager(cr, graph)
        for package in graph:
            migrations.migrate_module(package, 'end')

        # STEP 3.6: apply remaining constraints in case of an upgrade
        registry.finalize_constraints()

        # STEP 4: Finish and cleanup installations
        if processed_modules:
            env = api.Environment(cr, SUPERUSER_ID, {})
            cr.execute("""select model,name from ir_model where id NOT IN (select distinct model_id from ir_model_access)""")
            for (model, name) in cr.fetchall():
                if model in registry and not registry[model]._abstract:
                    _logger.warning('The model %s has no access rules, consider adding one. E.g. access_%s,access_%s,model_%s,base.group_user,1,0,0,0',
                        model, model.replace('.', '_'), model.replace('.', '_'), model.replace('.', '_'))

            cr.execute("SELECT model from ir_model")
            for (model,) in cr.fetchall():
                if model in registry:
                    env[model]._check_removed_columns(log=True)
                elif _logger.isEnabledFor(logging.INFO):    # more an info that a warning...
                    _logger.runbot("Model %s is declared but cannot be loaded! (Perhaps a module was partially removed or renamed)", model)

            # Cleanup orphan records
            env['ir.model.data']._process_end(processed_modules)
            env['base'].flush()

        for kind in ('init', 'demo', 'update'):
            tools.config[kind] = {}

        # STEP 5: Uninstall modules to remove
        if update_module:
            # Remove records referenced from ir_model_data for modules to be
            # removed (and removed the references from ir_model_data).
            cr.execute("SELECT name, id FROM ir_module_module WHERE state=%s", ('to remove',))
            modules_to_remove = dict(cr.fetchall())
            if modules_to_remove:
                env = api.Environment(cr, SUPERUSER_ID, {})
                pkgs = reversed([p for p in graph if p.name in modules_to_remove])
                for pkg in pkgs:
                    uninstall_hook = pkg.info.get('uninstall_hook')
                    if uninstall_hook:
                        py_module = sys.modules['odoo.addons.%s' % (pkg.name,)]
                        getattr(py_module, uninstall_hook)(cr, registry)

                Module = env['ir.module.module']
                Module.browse(modules_to_remove.values()).module_uninstall()
                # Recursive reload, should only happen once, because there should be no
                # modules to remove next time
                cr.commit()
                _logger.info('Reloading registry once more after uninstalling modules')
                api.Environment.reset()
                registry = odoo.modules.registry.Registry.new(
                    cr.dbname, force_demo, status, update_module
                )
                registry.check_tables_exist(cr)
                cr.commit()
                return registry

        # STEP 5.5: Verify extended fields on every model
        # This will fix the schema of all models in a situation such as:
        #   - module A is loaded and defines model M;
        #   - module B is installed/upgraded and extends model M;
        #   - module C is loaded and extends model M;
        #   - module B and C depend on A but not on each other;
        # The changes introduced by module C are not taken into account by the upgrade of B.
        if models_to_check:
            registry.init_models(cr, list(models_to_check), {'models_to_check': True})

        # STEP 6: verify custom views on every model
        if update_module:
            env = api.Environment(cr, SUPERUSER_ID, {})
            env['res.groups']._update_user_groups_view()
            View = env['ir.ui.view']
            for model in registry:
                try:
                    View._validate_custom_views(model)
                except Exception as e:
                    _logger.warning('invalid custom view(s) for model %s: %s', model, tools.ustr(e))

        if report.wasSuccessful():
            _logger.info('Modules loaded.')
        else:
            _logger.error('At least one test failed when loading the modules.')

        # STEP 8: call _register_hook on every model
        # This is done *exactly once* when the registry is being loaded. See the
        # management of those hooks in `Registry.setup_models`: all the calls to
        # setup_models() done here do not mess up with hooks, as registry.ready
        # is False.
        env = api.Environment(cr, SUPERUSER_ID, {})
        for model in env.values():
            model._register_hook()
        env['base'].flush()

        # STEP 9: save installed/updated modules for post-install tests
        registry.updated_modules += processed_modules

loading.load_module_graph = _load_module_graph
loading.load_marked_modules = _load_marked_modules
loading.load_modules = _load_modules
odoo.modules.load_modules = _load_modules
