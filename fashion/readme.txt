The goal of this module is to allow generic BOMs on products with the help of characteristics.

The typical use is garment industry with color and size as characteristics.

Generic BOMs helps you to manage the variety in mass customisation or assembly-to-order activities. You can design your products easily for the MRP system and improve correctness, completness and consistancy of your technical data.

Use those BOMs when you have sets of products very similar but some characteristics.
Use them also to turn business characteristics of sale products into technical characteristics 
This module can handle unlimited number of characteristics per product, but more than 2 is usually avoided (think about a greater than 2 dimensional space...).
Well known products have more: tree: bras (color and two sizes), cars (color, motor, options level), and four: windows (2 sizes, plastic/wood/aluminium, pane simple/double/double anti-reflecting )




data model:

characteristic group
	Group of homogeneous characteristics.
	color, size, diameter, level, power, option, capacity...
	axis is the prefered axis for layout (for fixed designation in specific reports or views)

characteristic
	blue,red, XL...
	magnitude should be used for sorting purpose in a group of characteristics (may be stature for sizes , hue for colors ...)

on template object
	group of characteristics (allowed on the variants)
	

on variant object
	characteristics (one for each group defined on the variant)
	group of the characteristics into a pool of same charateristics' type.


on BOM object
	variation lines to modify BOM behavior. 
	
Variation  variation  is a rule saying how a product's characteristic modifies the BOM behavior.
	parent's characteristic is to say when applying this rule.
	product's characteristic is the component's charateristic wanted (if any) 
	qty is the specific bom quantity if varying (overwrite the generic bom qty) (should be use as a  generic qty rate if generic qty not null)
	exclude? is to cancel the bom line 
	


explode bom method is   changed to follow variation lines on BOMs , to  give the right components.


example:

template shirt 
	allowed color and size characteristics

product variant shirt /none/
	as a generic product for the generic BOM

product variant shirt red XS
	color red, size XS

product variant shirt red XL
	color red, size XL

product variant shirt blue XS
	color blue, size XS


A phantom BOM is to create for each real product as an entry point of BOMs.
A dummy variant with no characteristic is to create for each template product, to allow generic BOM definition on it.

the generic BOM define components for the 4 variants

generic BOM on the /none/ variant
sub
	BOM fabric
		col red==red
		col blue==blue
		s XS qty 1
		s XL qty 2

	BOM button qty 8
		red==grey
		blue==grey
		s XS==diam 15mm
		s XL==diam 20mm 

	BOM embroidery "i love red" qty 1
		col blue exclude

product variant fabric /none/ 
	color blue 

product variant fabric blue 
	color blue 

product variant fabric red 
	color red 

product variant button /none/ 

product variant button  
	color grey, diameter 15mm 

product variant fabric blue 
	color grey, diameter 20mm

product BOM embroidery "i love red"


for exemple components explosion for "shirt blue xs"  give
-1(m) blue fabric 
-8 grey button  diam 15mm


