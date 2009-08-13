import netsvc
import pooler
import time
from report import report_sxw

class report_scrapie_2007(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_scrapie_2007, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,

        })

report_sxw.report_sxw('report.List_scrapie', 'labo.analysis.request', 'addons/labo_analysis/report/report_scrapie_2007.rml',parser=report_scrapie_2007)
