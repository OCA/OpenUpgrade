import time
import ir
from osv import osv
from report import report_sxw
import pooler

class loan_paper(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(loan_paper, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'merge' : self.__parse_paragraph__,
        })

    def __parse_paragraph__(self,content,loan):

        fetchval={
            '{p_name}':loan.name or '',
            '{p_loan_amount}':str(loan.loan_amount) or '',
            '{p_loan_period}':str(loan.loan_period) or '',
            '{p_process_fee}':str(loan.process_fee) or '',
            '{p_apply_date}':str(loan.apply_date) or '',
            '{p_approve_date}':str(loan.approve_date) or '',
            '{p_approve_amount}':str(loan.approve_amount) or '',
            '{p_contact}': str(loan.contact.name) + '\n' + str(loan.contact.street) + '\n ' + str(loan.contact.street2) + '\n ' + str(loan.contact.city) + '\n' + str(loan.contact.zip) or '',
        }
        for key in fetchval :
            content=content.replace(key,fetchval.get(key))
        return content;

report_sxw.report_sxw('report.letter.letter_info', 'account.loan', 'addons/loan/report/merge_letter.rml', parser=loan_paper)
