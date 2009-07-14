# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pooler
import time
import netsvc
import os
import os.path
import tools
from math import ceil
from psycopg2 import IntegrityError

##############################################################################
# Service to record use of the database
##############################################################################

objects_proxy = netsvc.SERVICES['object'].__class__

class recording_objects_proxy(objects_proxy):
    access_cache = {}
    HOUR_MINI = 1.0
    UNTIMED_CALLS = {
        # values are either '*' or a list of methods
        ## 'foo': ['bar', 'baz'],
        'res.request': '*',
    }
    def execute(self, db, uid, passwd, object, method, *args):
        cr = pooler.get_db(db).cursor()
        try:
            # check if database is blocked
            cr.execute('SELECT name FROM use_control_db_block')
            msg = cr.fetchone()
            if msg:
                self.abordResponse(None, 'Database suspended', 'warning', msg[0])

            utc = self.UNTIMED_CALLS.get(object, [])
            if utc is not '*' and method not in utc:

                cache = self.access_cache.setdefault(db, {})
                if (uid not in cache) or (cache[uid] < time.time()):
                    try:
                        cr.execute('INSERT INTO use_control_time (user_id, date, duration, active) VALUES (%s, now(), %s, %s)', 
                                    (int(uid), self.HOUR_MINI, True))
                    except IntegrityError, ie:
                        # if user does not exists do not record the time in the cache
                        pass
                    else:
                        cache[uid] = time.time() + 3600 * self.HOUR_MINI
                    cr.commit()

            return super(recording_objects_proxy, self).execute(db, uid, passwd, object, method, *args)
        finally:
            cr.close()

recording_objects_proxy()
        
##############################################################################
# Service to request feedback on a database usage
##############################################################################

class use_control_service(netsvc.Service):
    def __init__(self, name="use_control"):
        netsvc.Service.__init__(self, name)
        self.joinGroup("web-services")
        self.exportMethod(self.data_get)
        self.exportMethod(self.block)
        self.exportMethod(self.unblock)
        self.exportMethod(self.clean)

    def _get_size(self, cr, dbname):
        """Return the size of the system in Mb."""
        cr.execute('select pg_database_size(%s)', (dbname,))
        db_size = cr.fetchone()[0]
        dir_size = 0.0
        filestore = os.path.join(tools.config['root_path'], 'filestore', dbname)
        if os.path.isdir(filestore):
            for (path, dirs, files) in os.walk(filestore):
                for file in files:
                    filename = os.path.join(path, file)
                    dir_size += os.path.getsize(filename)
        r = float((dir_size + db_size) / (1024*1024) + 1.0) / 1024.0
        return ceil(r)

    def data_get(self, password, db):
        security.check_super(password)
        cr = pooler.get_db(db).cursor()
        cr.execute('''SELECT to_char(t.date, 'YYYY-MM-DD') as date,
                             u.name as username,
                             u.login as login,
                             sum(t.duration) as hours
                        FROM use_control_time t,
                             res_users u
                       WHERE u.id = t.user_id
                         AND t.active = %s
                         AND (uploaded = %s OR uploaded IS NULL)
                    GROUP BY to_char(t.date, 'YYYY-MM-DD'),
                             u.name,
                             u.login
                   ''', (True, False)
                   )
        data = cr.fetchall()
        cr.execute('UPDATE use_control_time SET uploaded=%s WHERE active = %s AND (uploaded = %s OR uploaded IS NULL)', (True, True, False))
        cr.execute('SELECT name FROM ir_module_module WHERE state=%s', ('installed',))
        modules = map(lambda x: x[0], cr.fetchall())

        hours = reduce(lambda x, y: x+y[3], data, 0.0)

        cr.execute('SELECT count(id) FROM res_users WHERE active = %s', (True,))
        users = cr.fetchone()[0]
        cr.execute('SELECT max(date) FROM use_control_time WHERE active = %s', (True,))
        maxdate = cr.fetchone()[0]
        result = {
            'details': data,
            'modules': modules,
            'latest_connection': maxdate or False,
            'users_number': users,
            'space': self._get_size(cr, db),
            'hours': hours,
        }
        cr.commit()
        cr.close()
        return result

    def block(self, password, dbname, message):
        security.check_super(password)
        db, pool = pooler.get_db_and_pool(dbname)
        cr = db.cursor()
        try:
            obj = pool.get('use.control.db.block')
            obj.create(cr, 1, {'name': message})
        finally:
            cr.commit()
            cr.close()
        return True

    def unblock(self, password, dbname):
        security.check_super(password)
        db, pool = pooler.get_db_and_pool(dbname)
        cr = db.cursor()
        try:
            obj = pool.get('use.control.db.block')
            obj.unlink(cr, 1, obj.search(cr, 1, []))
        finally:
            cr.commit()
            cr.close()
        return True
        
    def clean(self, password, dbname):
        security.check_super(password)
        cr = pooler.get_db(dbname).cursor()
        try:
            cr.execute('UPDATE use_control_time SET active = %s', (False,))
        finally:
            cr.commit()
            cr.close()
        return True

use_control_service()


