#
# Snippet to create a text field: just run it
#

import uno

localContext = uno.getComponentContext()

# create the UnoUrlResolver
resolver = localContext.ServiceManager.createInstanceWithContext(
				"com.sun.star.bridge.UnoUrlResolver", localContext )

# connect to the running office
ctx = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )
smgr = ctx.ServiceManager

desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
model = desktop.getCurrentComponent()

#xUserField = model.createInstance("com.sun.star.text.textField.User")
#print xUserField
xUserField = model.createInstance("com.sun.star.text.TextField.User")
xMasterPropSet = model.createInstance("com.sun.star.text.FieldMaster.User")
xMasterPropSet.setPropertyValue("Name", "UserEmperor")
xMasterPropSet.setPropertyValue("Content", "Fabien Pinckaers")
#xMasterPropSet.setPropertyValue("Content", uno.ByteSequence("UserEmperor"))

print xUserField, xMasterPropSet

xUserField.attachTextFieldMaster (xMasterPropSet)

text = model.Text
text.insertTextContent(text.getEnd(), xUserField, False)

