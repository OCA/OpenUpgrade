#!/usr/bin/python

import os
import sys
import StringIO
import psycopg2
import psycopg2.extensions
from optparse import OptionParser
from ConfigParser import SafeConfigParser
from bzrlib.branch import Branch
from bzrlib.repository import Repository
from bzrlib.workingtree import WorkingTree
import bzrlib.plugin
import bzrlib.builtins
import bzrlib.info

migrations={
  '7.0': {
      'addons': {
          'addons': 'lp:openupgrade-addons/7.0',
          'web': {'url': 'lp:openerp-web/7.0', 'addons_dir': 'addons'},
        },
      'server': {
          'url': 'lp:openupgrade-server/7.0', 
          'addons_dir': os.path.join('openerp','addons'),
          'root_dir': os.path.join(''),
          'cmd': 'openerp-server --update=all --database=%(db)s '+
            '--config=%(config)s --stop-after-init --no-xmlrpc --no-netrpc',
        },
    },
  '6.1': {
      'addons': {
          'addons': 'lp:openupgrade-addons/6.1',
          'web': {'url': 'lp:openerp-web/6.1', 'addons_dir': 'addons'},
        },
      'server': {
          'url': 'lp:openupgrade-server/6.1', 
          'addons_dir': os.path.join('openerp','addons'),
          'root_dir': os.path.join(''),
          'cmd': 'openerp-server --update=all --database=%(db)s '+
            '--config=%(config)s --stop-after-init --no-xmlrpc --no-netrpc',
        },
    },
  '6.0': {
      'addons': {
          'addons': 'lp:openupgrade-addons/6.0',
        },
      'server': {
          'url': 'lp:openupgrade-server/6.0',
          'addons_dir': os.path.join('bin','addons'),
          'root_dir': os.path.join('bin'),
          'cmd': 'bin/openerp-server.py --update=all --database=%(db)s '+
            '--config=%(config)s --stop-after-init --no-xmlrpc --no-netrpc',
        },
    },
}
config = SafeConfigParser()
parser = OptionParser(description="""Migrate script for the impatient or lazy.
Makes a copy of your database, downloads the files necessary to migrate
it as requested and runs the migration on the copy (so your original 
database will not be touched). While the migration is running only errors are 
shown, for a detailed log see ${branch-dir}/migration.log
""")
parser.add_option("-C", "--config", action="store", type="string", 
        dest="config", 
        help="current openerp config (required)")
parser.add_option("-D", "--database", action="store", type="string", 
        dest="database", 
        help="current openerp database (required if not given in config)")
parser.add_option("-B", "--branch-dir", action="store", type="string", 
        dest="branch_dir", 
        help="the directory to download openupgrade-server code to [%default]", 
        default='/var/tmp/openupgrade')
parser.add_option("-R", "--run-migrations", action="store", type="string", 
        dest="migrations", 
        help="comma separated list of migrations to run, ie. \""+
                ','.join(sorted([a for a in migrations]))+
                "\" (required)")
parser.add_option("-A", "--add", action="store", type="string", dest="add",
        help="load a python module that declares a dict 'migrations' which is "+
        "merged with the one of this script (see the source for details). "
        "You also can pass a string that evaluates to a dict. For the banking "
        "addons, pass "
        "\"{'6.1': {'addons': {'banking': 'lp:banking-addons/6.1'}}}\"")
parser.add_option("-I", "--inplace", action="store_true", dest="inplace",
        help="don't copy database before attempting upgrade (dangerous)")
(options, args) = parser.parse_args()

if (not options.config or not options.migrations 
        or not reduce(lambda a,b: a and (b in migrations), 
                        options.migrations.split(','), True)):
  parser.print_help()
  sys.exit()

config.read(options.config)

conn_parms = {}
for parm in ('host', 'port', 'user', 'password'):                             
    db_parm = 'db_' + parm
    if config.has_option('options', db_parm):
        conn_parms[parm] = config.get('options', db_parm)

if not 'user' in conn_parms:
    print 'No user found in configuration'
    sys.exit()
db_user = conn_parms['user']

db_name=options.database or config.get('options', 'db_name')

if not db_name or db_name=='' or db_name.isspace() or db_name.lower()=='false':
  parser.print_help()
  sys.exit()

conn_parms['database'] = db_name

if options.inplace:
  db=db_name
else:
  db=db_name+'_migrated'

if options.add:
    merge_migrations={}
    if os.path.isfile(options.add):
        import imp
        merge_migrations_mod=imp.load_source('merge_migrations_mod', 
                options.add)
        merge_migrations=merge_migrations_mod.migrations
    else:
        merge_migrations=eval(options.add)

    def deep_update(dict1, dict2):
        result={}
        for (name,value) in dict1.iteritems():
            if dict2.has_key(name):
                if isinstance(dict1[name], dict) and isinstance(dict2[name], 
                    dict):
                    result[name]=deep_update(dict1[name], dict2[name])
                else:
                    result[name]=dict2[name]
            else:
                result[name]=dict1[name]
        for (name,value) in dict2.iteritems():
            if name not in dict1:
                result[name]=value
        return result

    migrations=deep_update(migrations, merge_migrations)

for version in options.migrations.split(','):
    if version not in migrations:
        print '%s is not a valid version! (valid verions are %s)' % (version,
                ','.join(sorted([a for a in migrations])))

bzrlib.plugin.load_plugins()
bzrlib.trace.enable_default_logging()
logfile=os.path.join(options.branch_dir,'migration.log')

if not os.path.exists(options.branch_dir):
    os.mkdir(options.branch_dir)

for version in options.migrations.split(','):
    if not os.path.exists(os.path.join(options.branch_dir,version)):
        os.mkdir(os.path.join(options.branch_dir,version))
    for (name,url) in dict(migrations[version]['addons'], 
            server=migrations[version]['server']['url']).iteritems():
        link=url.get('link', False) if isinstance(url, dict) else False
        url=url['url'] if isinstance(url, dict) else url
        if os.path.exists(os.path.join(options.branch_dir,version,name)):
            if link:
                continue
            cmd_revno=bzrlib.builtins.cmd_revno()
            cmd_revno.outf=StringIO.StringIO()
            cmd_revno.run(location=os.path.join(options.branch_dir,version,
                name))
            print 'updating %s rev%s' %(os.path.join(version,name),
                    cmd_revno.outf.getvalue().strip())
            cmd_update=bzrlib.builtins.cmd_update()
            cmd_update.outf=StringIO.StringIO()
            cmd_update.outf.encoding='utf8'
            cmd_update.run(dir=os.path.join(options.branch_dir,version,
                name))
            if hasattr(cmd_update, '_operation'):
                cmd_update.cleanup_now()
            print 'now at rev'+cmd_revno.outf.getvalue().strip()
        else:
            if link:
                print 'linking %s to %s'%(url, 
                        os.path.join(options.branch_dir,version,name))
                os.symlink(url, os.path.join(options.branch_dir,version,name))
            else:
                print 'getting '+url
                cmd_checkout=bzrlib.builtins.cmd_checkout()
                cmd_checkout.outf=StringIO.StringIO()
                cmd_checkout.run(url, os.path.join(options.branch_dir,version,
                    name), lightweight=True)

if not options.inplace:
    print('copying database %(db_name)s to %(db)s...' % {'db_name': db_name, 
                                                         'db': db})
    conn = psycopg2.connect(**conn_parms)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur=conn.cursor()
    cur.execute('drop database if exists "%(db)s"' % {'db': db})
    try:
        print "Copying the database using 'with template'"
        cur.execute('create database "%(db)s" with template "%(db_name)s"' % {
            'db': db, 'db_name': db_name})
        cur.close()
    except psycopg2.OperationalError:
        print "Failed, fallback on creating empty database + loading a dump"
        cur.execute('create database "%(db)s"' % {'db': db})
        cur.close()

        os.environ['PGUSER'] = db_user             
        if ('host' in conn_parms and conn_parms['host']
                and not os.environ.get('PGHOST')):
            os.environ['PGHOST'] = conn_parms['host']             

        if ('port' in conn_parms and conn_parms['port']
                and not os.environ.get('PGPORT')):
            os.environ['PGPORT'] = conn_parms['port']             

        password_set = False
        if ('password' in conn_parms and conn_parms['password']
                and not os.environ.get('PGPASSWORD')):
            os.environ['PGPASSWORD'] = conn_parms['password']             
            password_set = True

        os.system(
            ('pg_dump --format=custom --no-password %(db_name)s ' +
             '| pg_restore --no-password --dbname=%(db)s') %
            {'db_name': db_name, 'db': db}
        )

        if password_set:
            del os.environ['PGPASSWORD'] 

for version in options.migrations.split(','):
  print 'running migration for '+version
  config.set('options', 'without_demo', 'True')
  config.set('options', 'logfile', logfile)
  config.set('options', 'port', 'False')
  config.set('options', 'netport', 'False')
  config.set('options', 'xmlrpc_port', 'False')
  config.set('options', 'netrpc_port', 'False')
  config.set('options', 'addons_path', 
   ','.join([os.path.join(options.branch_dir,
       version,'server',migrations[version]['server']['addons_dir'])] +
       [
           os.path.join(options.branch_dir,version,name,
               url.get('addons_dir', '') if isinstance(url, dict) else '') 
           for (name,url) in migrations[version]['addons'].iteritems()
       ]
       )
   )
  config.set('options', 'root_path', os.path.join(options.branch_dir,version,
      'server', migrations[version]['server']['root_dir']))
  config.write(open(
      os.path.join(options.branch_dir,version,'server.cfg'), 'w+'))
  os.system(
          os.path.join(options.branch_dir,version,'server',
              migrations[version]['server']['cmd'] % {
                  'db': db, 
                  'config': os.path.join(options.branch_dir,version,
                      'server.cfg')
                  }
              )
          )
