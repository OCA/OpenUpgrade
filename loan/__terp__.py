#!/usr/bin/env python
#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "Loan Management",
    "version" : "1.0",
    "depends" : ["base", "account", "account_voucher"],
    "author" : "Tiny",
    "description": """Loan Management System
    * Integrated to Accounting System
    * Usefull for any type of Loans - Home, Business, Personal
    * Clean Varification Process for Proofs 
    * Workflow for Loan Approval/Rejection
    * Reports related to the Loans, Documents, Loan Papers
    * Dynamic Interest Rates Calculation
    """,
    "website" : "http://www.tinyerpindia.com",
    "init_xml" : [],
    "demo_xml" : [
        "loan_demo.xml"
    ],
    "update_xml" : [
        "loan_view.xml",
        "loantype_view.xml",
        "loan_sequence.xml",
        "loan_report.xml",
        "loan_workflow.xml",
        "loan_wizard.xml",
        "cheque_workflow.xml",
    ],
    "active": False,
    "installable": True
}
