POS text printing format
===========================

POS printing is meant to provide a simple, generic solution for those
printers that need just raw text input (eg. ESC/POS ones), which need
not be processed by xml, xslt, rml etc. 

We hereby declare a simplistic text language, which will be the format
of the reports used for those operations. This language will be a text
segment, mainly supposed to be directly printed on the printer.

Escape sequences
-----------------

The escape sequences used will all start with a backslash \ or the
dollar sign $ . The template substitutions are inspired by the corresponding
Python function (see PEP-292)

The dollar sign can be escaped using either a $$ or a \$ sequence. In either
case, a single dollar character will be sent to the printer and subsequent
symbols will be parsed literally.
*-*

Report sections
-----------------
*Optionally*, the text "report" could be split into sections, so that
repetition loops (like the item lines in an invoice) or referenced
tables (like address of partner) can be accessed.

Each section should start **at a new line** with the characters: $\
i.e. percent + backslash.

If the report shall use any sections at all, then it **must** start with a
section. That is, the first characters of the report must be $\ .

After the section delimiter, in the same line, the name of the section must
follow. This will be either a Python identifier (any alpha+number combination,
not starting with a number), or an empty string for the main section. An
optional space can exist between the delimiter and the name.

A second argument after the name (separated by whitespace) could be used, to
indicate the data source for the section.

Eg. ::
	$\line account.line
	Item: $item       $price
	
	$\
	Main section
	
	$line
	

A named section, as showed above, will replace a variable with the same name,
in the main section. Note that multiple nesting is *not supported* yet. 

Perhaps such a feature could just implemented in the way the data is fed into
the report at the first stage.

