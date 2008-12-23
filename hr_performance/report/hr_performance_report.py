from report import report_sxw
import time
class performance_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(performance_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })
    
report_sxw.report_sxw(
        'report.hr_performance.report', 
        'hr.performance', 
        'addons/hr_performance/report/performance.rml', 
        parser=performance_report,
        header=False
)