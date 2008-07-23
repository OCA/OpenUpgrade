# -*- encoding: utf-8 -*-
import time
from report import report_sxw

class print_carnet(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(print_carnet, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.cci_missions_print_carnet', 'cci_missions.ata_carnet', 'addons/cci_mission/report/report_print_carnet.rml', parser=print_carnet,header=False)
report_sxw.report_sxw('report.cci_missions_print_carnet1', 'cci_missions.ata_carnet', 'addons/cci_mission/report/report_print_carnet1.rml', parser=print_carnet,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

