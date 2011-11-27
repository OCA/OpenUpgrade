The upgrade scripts for the 'account' module also cover its 'new' dependency 'analytic'.
TODO: will the OpenERP migration manager automatically select the 'analytic' module for installation?

account.acount: apply 'liquidity' as the internal account type for bank/cash accounts (can this be automated?)
account.journal: user need to set 'code' field for every journal
account.journal: Set journal type from 'cash' to 'bank' for bank journals
account.account.type: User needs to set the 'report_type'.

Other useful settings you might want to review:
      account.journal: 'Check date not in period'

