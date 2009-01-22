{
	"name" : "Account Regularizations",
	"version" : "1.0",
	"author" : "ACYSOS S.L.",
	"description" : """ This module creates a new object in accounting, 
	very similar to the account models named account.regularization. 
	Within this object you can define regularization moves, 
	This is, accounting moves that will automatically calculate the balance of a set of accounts, 
	Set it to 0 and transfer the difference to a new account. This is used, for example with tax declarations or in some countries to create the 'Profit and Loss' regularization
""",
	"category" : "Accounting",
	"depends" : ["account"],
	"demo_xml" : [],
	"update_xml" : [
		"account_regularization_view.xml",
		"account_wizard.xml",
		"security/ir.model.access.csv"
	],
	"active": False,
	"installable": True,

}
