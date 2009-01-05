from turbogears.widgets import Widget
from turbogears.widgets import JSLink

class MochiKit(Widget):
    javascript = [JSLink("erpcomparator", "javascript/MochiKit/MochiKit.js"),
                  JSLink("erpcomparator", "javascript/MochiKit/DragAndDrop.js"),
                  JSLink("erpcomparator", "javascript/MochiKit/Resizable.js"),
                  JSLink("erpcomparator", "javascript/MochiKit/Sortable.js")]

mochikit = MochiKit()

