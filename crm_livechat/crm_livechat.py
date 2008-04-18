from osv import fields,osv
from osv import orm
import pooler
import time

class crm_livechat_jabber(osv.osv):
	_name="crm_livechat.jabber"
	_description= "Livechat Account"
	_columns={
		'name': fields.char("Jabber Account", size=128, required=True),
		'server': fields.char('Jabber Server', size=40, required=True),
		'login': fields.char('Account Login', size=32, required=True),
		'password': fields.char('Account Password', size=16, required=True),
	}
crm_livechat_jabber()


#
# When a visitor wants to talk, he has to call start_session
# Then close_session when it's finnished
#
class crm_livechat_livechat(osv.osv):
	_name="crm_livechat.livechat"
	_description= "LiveChat Account"
	_columns={
		'name': fields.char("Livechat Account", size=128, required=True),
		'state': fields.selection([('active','Active'),('notactive','Not Active')], "State"),
		'max_per_user': fields.integer('Maximum Customer per User'),
		'session_delay': fields.integer('Minutes to Close a session', help="Put here to number of minutes after which a session is considered as closed"),
		'user_ids': fields.one2many('crm_livechat.livechat.user', 'livechat_id', 'Users Accounts'),
		'partner_ids': fields.one2many('crm_livechat.livechat.partner', 'livechat_id', 'Visitors Accounts'),
	}
	_defaults = {
		'max_per_user': lambda *args: 5,
		'state': lambda *args: 'notactive'
	}
	def __init__(self, *args, **argv):
		self.session_count = 0
		self.sessions = {}
		return super(crm_livechat_livechat, self).__init__(*args, **argv)

	#
	# return { jabber_id, {jabber_connection_data} }
	#
	def get_configuration(self, cr, uid, ids, context={}):
		result = {}
		for lc in self.browse(cr, uid, ids, context):
			for u in lc.user_ids + lc.partner_ids:
				result[u.jabber_id.id] = {
					'name': u.name,
					'server': u.jabber_id.server,
					'login':  u.jabber_id.login,
					'password':  u.jabber_id.password,
				}
		return result

	def get_user(self, cr, uid, id, context={}):
		minu = (9999999,False)
		livechat = self.browse(cr, uid, id)
		for user in livechat.user_ids:
			if not user.state==available:
				continue
			c = 0
			for s in self.sessions:
				if s[0]==user.user_id.id:
					c+=1
			if c<minu[0]:
				if c<livechat.max_per_user:
					minu = (c, user.user_id.id)
		return minu[1]

	"""
		IN:
			livechat_id
			user_id : False (auto-detect) or force a particular user
			partner_ip: IP Address of the partner
			lang: language of the partner (False for unknown)
		OUT:
			False if no available users or partners
			(session_id, user_jabber_id, partner_jabber_id) if available
	"""
	def start_session(self, cr, uid, livechat_id, user_id=False, partner_ip='Unknown', lang=False, context={}):
		if not user_id:
			user_id = self.get_user(cr, uid, livechat_id, context)
		if not user_id:
			return False

		partner_id=False
		for p in self.browse(cr, uid, livechat_id, context).partner_ids:
			if not p.available:
				partner_id = p.jabber_id.id
		if not partner_id:
			return False
		self.pool.get('crm_livechat.livechat.partner').write(cr, uid, [partner_id], {
			'available': partner_ip,
			'available_date': time.strftime('%Y-%m-%d %H:%M:%S')
		})
		self.session_count+=1
		self.sessions[self.session_count] = (user_id, partner_id, livechat_id)
		return True

	"""
		IN:
			livechat_id
			session_id : The ID of a session
		OUT:
			True
	"""
	def stop_session(self, cr, uid, id, session_id, log=False, context={}):
		self.pool.get('crm_livechat.livechat.partner').write(cr, uid, [partner_id], {
			'available': False,
		})
		if session_id in self.sessions:
			if log:
				self.pool.get('crm_livechat.log').create(cr, uid, {
					'note': log,
					'user_id': self.sessions[session_id][0],
					'livechat_id':self.sessions[session_id][2],
				})
			del self.sessions[session_id]
		return True

crm_livechat_livechat()

class crm_livechat_livechat_partner(osv.osv):
	_name="crm_livechat.livechat.partner"
	_description= "LiveChat Partners"
	_columns={
		'name': fields.char("Account Name", size=128, required=True),
		'jabber_id': fields.many2one('crm_livechat.jabber', "Jabber Account", required=True),
		'livechat_id': fields.many2one("crm_livechat.livechat", "Livechat", required=True),
		'available': fields.char('Available IP', size=64),
		'available_date': fields.datetime('Available Date'),
		'state': fields.selection([('active','Active'),('notactive','Not Active')], "State", required=True),
	}
	_defaults = {
		'state': lambda *args: 'notactive'
	}
crm_livechat_livechat_partner()

class crm_livechat_livechat_user(osv.osv):
	_name="crm_livechat.livechat.user"
	_description= "LiveChat Users"
	_columns={
		'name': fields.char("User Name", size=128, required=True),
		'user_id': fields.many2one('res.users', "User", required=True),
		'jabber_id': fields.many2one('crm_livechat.jabber', "Jabber Account", required=True),
		'livechat_id': fields.many2one("crm_livechat.livechat", "Livechat", required=True),
		'languages': fields.char('Language Regex', size=128),
		'state': fields.selection([('active','Active'),('notactive','Not Active')], "State", required=True),
	}
	_defaults = {
		'state': lambda *args: 'notactive'
	}
crm_livechat_livechat_user()

class crm_livechat_livechat_log(osv.osv):
	_name="crm_livechat.log"
	_description= "LiveChat Log"
	_order = 'id desc'
	_columns={
		'name': fields.datetime("Date and Time", required=True),
		'user_id': fields.many2one('res.users', "User"),
		'livechat_id': fields.many2one("crm_livechat.livechat", "Livechat", required=True, ondelete='cascade'),
		'note': fields.text('History')
	}
	_defaults = {
		'name': lambda *args: time.strftime('%Y-%m-%d %H:%M:%S')
	}
crm_livechat_livechat_log()



