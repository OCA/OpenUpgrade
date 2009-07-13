{
    "name" : "Google translation",
    "version": "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/Others",
    "depends" : ["base"],
    "description": '''Module create wizard on ir.translation object for Tranlslation of its terms using google,
you can also find menu at Administration/Translation/Application Terms/All terms/ Need review terms''',
    "init_xml" : [],
    "update_xml": ["google_translate_view.xml", "google_translate_wizard.xml"],
    "active": False,
    "installable": True
}