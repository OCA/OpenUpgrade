#
# Insert text at the current cursor position
#

import uno

localContext = uno.getComponentContext()
resolver = localContext.ServiceManager.createInstanceWithContext(
				"com.sun.star.bridge.UnoUrlResolver", localContext )
ctx = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )
smgr = ctx.ServiceManager

desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
model = desktop.getCurrentComponent()

controller = model.getCurrentController()
cursor = controller.getViewCursor()

text = model.Text
text.insertString(cursor, "bla", False)
ctx.ServiceManager
