# -*- encoding: utf-8 -*-
import wizard
import pooler

def _campaign_tasks(self, cr, uid, data, context):
    campaign_id = data['id']
    cr.execute('''SELECT project_id FROM dm_campaign WHERE id = %d '''% (campaign_id, ))
    res = cr.fetchone()
    if not res[0]:
        raise wizard.except_wizard('Error !', 'No project defined for this campaign. You can create one with the retro-planning button !')
    value = {
        'domain': [('project_id', '=', res[0])],
        'name': 'Tasks',
        'view_type': 'form',
        'view_mode': 'tree,form,calendar',
        'res_model': 'project.task',
        'context': { },
        'type': 'ir.actions.act_window'
    }
    return value

class wizard_campaign_tasks(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': _campaign_tasks,
                'state': 'end'
            }
        },
    }
wizard_campaign_tasks("wizard_campaign_tasks")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
