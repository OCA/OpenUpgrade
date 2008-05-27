##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv, fields

VoteValues = [('0','Very Bad'),('25', 'Bad'),('50','None'),('75','Good'),('100','Very Good') ]
DefaultVoteValue = '50'
MaximumVoteValue = '100'

class idm_idea(osv.osv):
        _name = 'idm.idea'
        _rec_name = 'title'

        def _compute_avg(self, cr, uid, ids, name, arg, context = None):
                res={}
                if not len(ids):
                    return res
                
                sql = """
                select idm_vote.idea_id as id, avg( cast( idm_vote.score as integer ) ) as avg 
                  from idm_vote 
                 where idm_vote.idea_id in (%s)
                 group by idm_vote.idea_id
                """ % ','.join(map(str, ids))
                
                cr.execute(sql)
                for id, avg in cr.fetchall():
                        res[id] = avg

                return res

        def _read_my_vote(self, cr, uid, ids, name, arg, context = None):
                res={}
                vote_obj = self.pool.get('idm.vote')
                for id in ids:
                        res[id]= DefaultVoteValue
                        votes_ids = vote_obj.search(cr, uid, [('idea_id', '=', id), ('user_id', '=', uid)])
                        if votes_ids:
                                res[id] = vote_obj.read(cr, uid, [votes_ids[0]], ['score'])[0]['score']

                return res

        def _save_my_vote(self, cr, uid, id, field_name, field_value, arg, context = None):
                vote_obj = self.pool.get('idm.vote')
                vote = vote_obj.search(cr,uid,[('idea_id', '=', id),('user_id', '=', uid)])
                textual_value = str(field_value)
                if vote:
                        vote_obj.write(cr,uid, vote[0], { 'score' : textual_value })
                else:
                        vote_obj.create(cr,uid, { 'idea_id' : id, 'user_id' : uid, 'score' : textual_value })

        _columns = {
                'user_id': fields.many2one('res.users', 'Creator', required=True, readonly=True),
                'title': fields.char('Title', size=64, required=True),
                'description': fields.text('Description', required=True, help='Content of the idea'),
                'comment_ids': fields.one2many('idm.comment', 'idea_id', 'Comments'),
                'create_date' : fields.datetime( 'Creation date', readonly=True),
                'vote_ids' : fields.one2many('idm.vote', 'idea_id', 'Vote'),
                'my_vote' : fields.function(_read_my_vote, fnct_inv = _save_my_vote, string="My Vote", method=True, type="selection", selection=VoteValues),
                'vote_avg' : fields.function(_compute_avg, method=True, string="Average", type="float", selection=VoteValues),
        }

        _defaults = {
                'user_id': lambda self,cr,uid,context: uid,
                'my_vote': lambda *a: MaximumVoteValue,
        }

        _order = 'create_date desc'


idm_idea()

class idm_comment(osv.osv):
        _name = 'idm.comment'
        _description = 'Comments'
        _rec_name = 'content'
        _columns = {
                'idea_id': fields.many2one('idm.idea', 'Idea', required=True, ondelete='cascade' ),
                'user_id': fields.many2one('res.users', 'User', required=True ),
                'content': fields.text( 'Content', required=True ),
        }
        _defaults = {
                'user_id': lambda self, cr, uid, context: uid
        }
        _order = 'create_date' 

idm_comment()

class idm_vote(osv.osv):
        _name = 'idm.vote'
        _rec_name = 'score'
        _columns = {
                'user_id': fields.many2one( 'res.users', 'User', required=True),
                'idea_id': fields.many2one('idm.idea', 'Idea', required=True, ondelete='cascade'),
                'score': fields.selection( VoteValues, 'Score', required=True)
        }
        _defaults = {
                'score': lambda *a: DefaultVoteValue,
        }

idm_vote()
