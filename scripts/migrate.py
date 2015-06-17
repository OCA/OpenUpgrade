#!/usr/bin/env python2

import os
import sys
import StringIO
import psycopg2
import psycopg2.extensions
from optparse import OptionParser
from ConfigParser import SafeConfigParser
try:
    import bzrlib.plugin
    import bzrlib.builtins
except ImportError:
    pass


def copy_database(conn_parms):
    db_old = conn_parms['database']
    db_new = '%s_migrated' % conn_parms['database']
    print('copying database %(db_old)s to %(db_new)s...' % {'db_old': db_old,
                                                            'db_new': db_new})
    if conn_parms.get('host') == 'False':
        del conn_parms['host']
        del conn_parms['port']
    conn = psycopg2.connect(**conn_parms)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('drop database if exists "%(db)s"' % {'db': db_new})
    try:
        print "Copying the database using 'with template'"
        cur.execute('create database "%(db_new)s" with template "%(db_old)s"' %
                    {'db_new': db_new, 'db_old': db_old})
        cur.close()
    except psycopg2.OperationalError:
        print "Failed, fallback on creating empty database + loading a dump"
        cur.execute('create database "%(db)s"' % {'db': db_new})
        cur.close()

        os.environ['PGUSER'] = conn_parms['user']
        if conn_parms.get('host') and not os.environ.get('PGHOST'):
            os.environ['PGHOST'] = conn_parms['host']

        if conn_parms.get('port') and not os.environ.get('PGPORT'):
            os.environ['PGPORT'] = conn_parms['port']

        password_set = False
        if conn_parms.get('password') and not os.environ.get('PGPASSWORD'):
            os.environ['PGPASSWORD'] = conn_parms['password']
            password_set = True

        os.system(
            ('pg_dump --format=custom --no-password %(db_old)s ' +
             '| pg_restore --no-password --dbname=%(db_new)s') %
            {'db_old': db_old, 'db_new': db_new}
        )

        if password_set:
            del os.environ['PGPASSWORD']
    return db_new

migrations = {
    '8.0': {
        'addons': {
            'addons': {
                'type': 'link',
                'url': os.path.join('server', 'addons'),
            },
        },
        'server': {
            'type': 'git',
            'url': 'git://github.com/OpenUpgrade/OpenUpgrade.git',
            'branch': '8.0',
            'addons_dir': os.path.join('openerp', 'addons'),
            'root_dir': os.path.join(''),
            'cmd': 'openerp-server --update=all --database=%(db)s '
                   '--config=%(config)s --stop-after-init --no-xmlrpc',
            },
    },
    '7.0': {
        'addons': {
            'addons': {
                'type': 'link',
                'url': os.path.join('server', 'addons'),
            },
        },
        'server': {
            'type': 'git',
            'url': 'git://github.com/OpenUpgrade/OpenUpgrade.git',
            'branch': '7.0',
            'addons_dir': os.path.join('openerp', 'addons'),
            'root_dir': os.path.join(''),
            'cmd': 'openerp-server --update=all --database=%(db)s '
                   '--config=%(config)s --stop-after-init --no-xmlrpc '
                   '--no-netrpc',
        },
    },
    '6.1': {
        'addons': {
            'addons': {
                'type': 'link',
                'url': os.path.join('server', 'addons'),
            },
        },
        'server': {
            'type': 'git',
            'url': 'git://github.com/OpenUpgrade/OpenUpgrade.git',
            'branch': '6.1',
            'addons_dir': os.path.join('openerp', 'addons'),
            'root_dir': os.path.join(''),
            'cmd': 'openerp-server --update=all --database=%(db)s '
                   '--config=%(config)s --stop-after-init --no-xmlrpc '
                   '--no-netrpc',
        },
    },
    '6.0': {
        'addons': {
            'addons': {
                'type': 'link',
                'url': os.path.join('server', 'addons'),
            },
        },
        'server': {
            'type': 'git',
            'url': 'git://github.com/OpenUpgrade/OpenUpgrade.git',
            'branch': '6.0',
            'addons_dir': os.path.join('bin', 'addons'),
            'root_dir': os.path.join('bin'),
            'cmd': 'bin/openerp-server.py --update=all --database=%(db)s '
                   '--config=%(config)s --stop-after-init --no-xmlrpc '
                   '--no-netrpc',
        },
    },
}
config = SafeConfigParser()
parser = OptionParser(
    description='Migrate script for the impatient or lazy. '
    'Makes a copy of your database, downloads the files necessary to migrate '
    'it as requested and runs the migration on the copy (so your original '
    'database will not be touched). While the migration is running only '
    'errors are shown, for a detailed log see ${branch-dir}/migration.log')
parser.add_option(
    "-C", "--config", action="store", type="string",
    dest="config",
    help="current openerp config (required)")
parser.add_option(
    "-D", "--database", action="store", type="string",
    dest="database",
    help="current openerp database (required if not given in config)")
parser.add_option(
    "-B", "--branch-dir", action="store", type="string",
    dest="branch_dir",
    help="the directory to download openupgrade-server code to [%default]",
    default='/var/tmp/openupgrade')
parser.add_option(
    "-R", "--run-migrations", action="store", type="string",
    dest="migrations",
    help="comma separated list of migrations to run, ie. \"" +
    ','.join(sorted([a for a in migrations])) +
    "\" (required)")
parser.add_option(
    "-A", "--add", action="store", type="string", dest="add",
    help="load a python module that declares a dict "
    "'migrations' which is merged with the one of this script "
    "(see the source for details). You also can pass a string "
    "that evaluates to a dict. For the banking addons, pass "
    "\"{'6.1': {'addons': {'banking': 'lp:banking-addons/6.1'}}}\"")
parser.add_option("-I", "--inplace", action="store_true", dest="inplace",
                  help="don't copy database before attempting upgrade "
                  "(dangerous)")
parser.add_option(
    "-F", "--force-deps", action="store", dest="force_deps",
    help="force dependencies from a dict of the form \"{'module_name': "
    "['new_dependency1', 'new_dependency2']}\"")
(options, args) = parser.parse_args()

if not options.config or not options.migrations\
        or not reduce(lambda a, b: a and (b in migrations),
                      options.migrations.split(','),
                      True):
    parser.print_help()
    sys.exit()

config.read(options.config)

conn_parms = {}
for parm in ('host', 'port', 'user', 'password'):
    db_parm = 'db_' + parm
    if config.has_option('options', db_parm):
        conn_parms[parm] = config.get('options', db_parm)

if 'user' not in conn_parms:
    print 'No user found in configuration'
    sys.exit()

db_name = options.database or config.get('options', 'db_name')

if not db_name or db_name == '' or db_name.isspace()\
        or db_name.lower() == 'false':
    parser.print_help()
    sys.exit()

conn_parms['database'] = db_name

if options.force_deps:
    try:
        eval(options.force_deps)
    except:
        parser.print_help()
        sys.exit()

if options.add:
    merge_migrations = {}
    if os.path.isfile(options.add):
        import imp
        merge_migrations_mod = imp.load_source('merge_migrations_mod',
                                               options.add)
        merge_migrations = merge_migrations_mod.migrations
    else:
        try:
            merge_migrations = eval(options.add)
        except:
            parser.print_help()
            sys.exit()

    def deep_update(dict1, dict2):
        result = {}
        for (name, value) in dict1.iteritems():
            if name in dict2:
                if isinstance(dict1[name], dict) and isinstance(dict2[name],
                                                                dict):
                    result[name] = deep_update(dict1[name], dict2[name])
                else:
                    result[name] = dict2[name]
            else:
                result[name] = dict1[name]
        for (name, value) in dict2.iteritems():
            if name not in dict1:
                result[name] = value
        return result

    migrations = deep_update(migrations, merge_migrations)

for version in options.migrations.split(','):
    if version not in migrations:
        print '%s is not a valid version! (valid verions are %s)' % (
            version,
            ','.join(sorted([a for a in migrations])))

bzrlib.plugin.load_plugins()
bzrlib.trace.enable_default_logging()
logfile = os.path.join(options.branch_dir, 'migration.log')

if not os.path.exists(options.branch_dir):
    os.mkdir(options.branch_dir)

for version in options.migrations.split(','):
    if not os.path.exists(os.path.join(options.branch_dir, version)):
        os.mkdir(os.path.join(options.branch_dir, version))
    for (name, addon_config) in dict(
            migrations[version]['addons'],
            server=migrations[version]['server']).iteritems():
        addon_config = addon_config\
            if isinstance(addon_config, dict)\
            else {'url': addon_config}
        addon_config_type = addon_config.get('type', 'bzr')
        target = os.path.join(options.branch_dir, version, 'rep_addons', name)
        if os.path.exists(target):
            if addon_config_type == 'link':
                continue
            elif addon_config_type == 'bzr':
                cmd_revno = bzrlib.builtins.cmd_revno()
                cmd_revno.outf = StringIO.StringIO()
                cmd_revno.run(location=target)
                print 'updating %s rev%s' % (
                    os.path.join(version, name),
                    cmd_revno.outf.getvalue().strip())
                cmd_update = bzrlib.builtins.cmd_update()
                cmd_update.outf = StringIO.StringIO()
                cmd_update.outf.encoding = 'utf8'
                cmd_update.run(
                    dir=target)
                if hasattr(cmd_update, '_operation'):
                    cmd_update.cleanup_now()
                print 'now at rev' + cmd_revno.outf.getvalue().strip()
            elif addon_config_type == 'git':
                os.system('cd %(location)s; git pull origin %(branch)s' % {
                    'branch': addon_config.get('branch', 'master'),
                    'location': target,
                })
            else:
                raise Exception('Unknown type %s' % addon_config_type)
        else:
            if addon_config_type == 'link':
                print 'linking %s to %s' % (addon_config['url'], target)
                os.symlink(addon_config['url'], target)
            elif addon_config_type == 'bzr':
                print 'getting ' + addon_config['url']
                cmd_checkout = bzrlib.builtins.cmd_checkout()
                cmd_checkout.outf = StringIO.StringIO()
                cmd_checkout.run(
                    addon_config['url'],
                    target,
                    lightweight=True)
            elif addon_config_type == 'git':
                print 'getting ' + addon_config['url']
                os.system('git clone --branch %(branch)s --single-branch '
                          '--depth=1 %(url)s %(target)s' %
                          {
                              'branch': addon_config.get('branch', 'master'),
                              'url': addon_config['url'],
                              'target': target,
                          })
            else:
                raise Exception('Unknown type %s' % addon_config_type)

        realtarget = os.path.realpath(target)
        for root, dirs, files in os.walk(realtarget):
            for file in files:
                if file == "__openerp__.py":
                    linkpath = os.path.join(options.branch_dir,
                                            version, 'addons', name)
                    if os.path.exists(linkpath):
                        os.remove(linkpath)
                    os.symlink(root, linkpath)

db_name = conn_parms['database']
if not options.inplace:
    db_name = copy_database(conn_parms)

for version in options.migrations.split(','):
    print 'running migration for '+version
    config.set('options', 'without_demo', 'True')
    config.set('options', 'logfile', logfile)
    config.set('options', 'port', 'False')
    config.set('options', 'netport', 'False')
    config.set('options', 'xmlrpc_port', 'False')
    config.set('options', 'netrpc_port', 'False')
    config.set(
        'options',
        'addons_path',
        ','.join(
            [os.path.realpath(os.path.join(options.branch_dir,
                          version,
                          'addons'))] +
            []))
    config.set(
        'options',
        'root_path',
        os.path.join(
            options.branch_dir,
            version,
            'server',
            migrations[version]['server']['root_dir']))
    if options.force_deps:
        if not config.has_section('openupgrade'):
            config.add_section('openupgrade')
        config.set('openupgrade', 'force_deps', options.force_deps)
    config.write(
        open(
            os.path.join(options.branch_dir, version, 'server.cfg'), 'w+'))

    os.system(
        os.path.join(
            options.branch_dir,
            version,
            'server',
            migrations[version]['server']['cmd'] % {
                'db': db_name,
                'config': os.path.join(options.branch_dir, version,
                                       'server.cfg')
            }))
