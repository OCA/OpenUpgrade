from c2c_reporting_tools.reports.standard_report import StandardReport
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


class myReport(StandardReport):     

    
    def get_story(self):
        return [Paragraph("Hello World",ParagraphStyle("dummy"))]

    
myReport('report.hello_world_c2c_reporting_tools', "Hello Word with c2c reporting tools", None, myReport.A4_PORTRAIT)        