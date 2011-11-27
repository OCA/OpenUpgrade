The upgrade scripts for the 'account' module also cover its 'new' dependency 'analytic'.
TODO: will the OpenERP migration manager automatically select the 'analytic' module for installation?

Data integrity
==============
account.acount: apply 'liquidity' as the internal account type for bank/cash accounts (can this be automated?)
account.journal: user need to set 'code' field for every journal
account.journal: Set journal type from 'cash' to 'bank' for bank journals
account.account.type: User needs to set the 'report_type'.

Other useful settings you might want to review:
      account.journal: 'Check date not in period'

Journal view columns
====================
The account module contains a special configuration of columns for every journal type. This upgrade script adds the following columns:

    Bank journal view: Reconcile
    Bank journal Multi view: Reconcile

In OpenERP 6, the following columns are not visible by default anymore:
   Bank journal view: Tax
   Journal view: Maturity date, Tax, Tax Account and Tax amount

You may want to remove these columns manually from their respective view types.

Permissions and rights
======================
OpenERP 6 adds a new group, Analytic Accounting. Add the relevant users to this group.
