import pooler
import time
import netsvc

##############################################################################
# Service to record use of the database
##############################################################################

HOUR_MINI = 1.0

def check(chk_fnct):
    data = {}
    def check_one(db, uid, passwd):
        data.setdefault(db, {})
        if (uid not in data) or (data[uid]<time.time()):
            data[uid] = time.time() + 3600 * HOUR_MINI
            cr = pooler.get_db(db).cursor()
            try:
                cr.execute('insert into use_control_time (user_id, date, duration) values (%s,%s,%s)', (int(uid), time.strftime('%Y-%m-%d %H:%M:%S'), HOUR_MINI))
                cr.commit()
            except:
                pass
            cr.close()
        return chk_fnct(db, uid, passwd)
    return check_one

# May be it's better using inheritancy and resubscribing the service
# Override the check method to store use of the database
from service import security
security.check = check(security.check)

##############################################################################
# Service to request feedback on a database usage
##############################################################################

class use_control_service(netsvc.Service):
    def __init__(self, name="use_control"):
        netsvc.Service.__init__(self, name)
        self.joinGroup("web-services")
        self.exportMethod(self.data_get)
    def data_get(self, password, dbname, date_from=False, date_to=False):
        security.check_super(password)
        return {
            'details': [
                {'user':'Administrator', 'login': 'admin', 'duration': 12},
                {'user':'Demo User', 'login': 'demo', 'duration': 12},
            ],
            'modules': [
                'base', 'sale', 'use_control'
            ],
            'latest_connection': '2009-01-01 12:30:01',
            'users_number': 4,
            'space': 123,
            'hours': 12,
        }
use_control_service()


