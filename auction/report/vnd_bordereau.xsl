<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">
	<xsl:import href="../../custom/corporate_defaults.xsl"/>
		<xsl:import href="../../base/report/rml_template.xsl"/>

	<xsl:template match="/">
		<xsl:call-template name="rml"/>
	</xsl:template>

	<xsl:template name="stylesheet">
		<paraStyle name="name" fontName="Helvetica-Bold" fontSize="16"/>
		<blockTableStyle id="products">
			 <blockFont name="Helvetica-BoldOblique" size="12" start="0,0" stop="-1,0"/>
			 <lineStyle kind="LINEBELOW" start="0,0" stop="-1,0"/>
			 <blockValign value="TOP"/>
			 <blockAlignment value="RIGHT" start="-1,0" stop="-1,-1"/>
		</blockTableStyle>
		<paraStyle name="style1" fontName="Helvetica" fontSize="12" alignment="RIGHT"/>
		<blockTableStyle id="product-totals">
			 <blockValign value="TOP"/>
			 <blockAlignment value="RIGHT"/>
			 <lineStyle kind="LINEABOVE" start="-1,0" stop="-1,0"/>
			 <lineStyle kind="LINEABOVE" start="-1,-1" stop="-1,-1"/>
		</blockTableStyle>
	</xsl:template>

	<xsl:template name="story">
		<xsl:apply-templates select="vente-bordereau-list"/>
	</xsl:template>

	<xsl:template match="vente-bordereau-list">
		<xsl:apply-templates select="vente-bordereau">
			<xsl:sort order="ascending" select="inventory"/>
		</xsl:apply-templates>
	</xsl:template>
	<xsl:template match="vente-bordereau">
		<nextFrame/>
		<setNextTemplate name="other_pages"/>
			<xsl:apply-templates select="client_info"/>
			<spacer length="0.8cm"/>
		<para>
			<b t="1">Document</b>: <xsl:value-of select="subject"/> - <xsl:value-of select="title"/>
		</para>
		<para>
			<b t="1">Inventory</b>: <xsl:value-of select="inventory"/>
		</para>

		<xsl:if test="client_info">
			<para>
<!--				<b t="1">Bank Account</b>: <xsl:value-of select="client_info/bank"/>-->
			</para><para>
<!--				<b t="1">Customer Contact</b>:-->
				<xsl:value-of select="client_info/phone"/>
				<xsl:if test="number(string-length(client_info/phone) &gt; 0) + number(string-length(client_info/mobile) &gt; 0) = 2">
					<xsl:text> - </xsl:text>
				</xsl:if>
				<xsl:value-of select="client_info/mobile"/>
			</para>
		</xsl:if>

		<spacer length="0.8cm"/>

		<xsl:apply-templates select="vente-products"/>

<!--		<setNextTemplate name="first_page"/>-->
<!--		<pageBreak/>-->
	</xsl:template>

	<xsl:template match="client_info">
		<para style="style1">
			<b>
				<xsl:value-of select="title"/>
				<xsl:text> </xsl:text>
				<xsl:value-of select="name"/>
			</b>
		</para>
		<para style="style1"><xsl:value-of select="street"/></para>
		<para style="style1"><xsl:value-of select="street2"/></para>
		<para style="style1">
			<xsl:value-of select="zip"/>
			<xsl:text> </xsl:text>
			<xsl:value-of select="city"/>
		</para>
		<para style="style1"><xsl:value-of select="country"/></para>
	</xsl:template>

	<xsl:template match="vente-products">
		<blockTable colWidths="2.0cm,2.0cm,12.0cm,2.4cm" style="products">
			<tr>
				<td t="1">Cat. N.</td><td t="1">List N.</td><td t="1">Description</td><td t="1">Adj.(EUR)</td>
			</tr>
			<xsl:apply-templates select="product">
				<xsl:sort order="ascending" data-type="number" select="num_catalog"/>
			</xsl:apply-templates>
		</blockTable>
		<condPageBreak height="3.2cm"/>
		<blockTable colWidths="2.0cm,2.0cm,12.0cm,2.4cm" style="product-totals">
			<tr>
				<td/>
				<td/>
				<td t="1">Subtotal:</td>
				<td><xsl:value-of select="format-number(sum(product[price != '']/price), '#,##0.00')"/></td>
			</tr>
			<xsl:apply-templates select="cost">
				<xsl:sort data-type="number" select="type"/>
				<xsl:sort data-type="number" select="id"/>
			</xsl:apply-templates>
			<tr>
				<td/>
				<td/>
				<td t="1">Total:</td>
				<td><xsl:value-of select="format-number(sum(product[price != '']/price) + sum(cost/amount), '#,##0.00')"/></td>
			</tr>
		</blockTable>
	</xsl:template>

	<xsl:template match="cost">
		<tr>
			<td/>
			<td/>
			<td><xsl:value-of select="name"/>:</td>
			<td><xsl:value-of select="format-number(amount, '#,##0.00')"/></td>
		</tr>
	</xsl:template>

	<xsl:template match="product">
		<tr>
			<td><xsl:value-of select="num_catalog"/></td>
			<td><xsl:value-of select="num_inv"/></td>
			<td><para><b><xsl:value-of select="title"/></b></para></td>
			<td>
				<xsl:choose>
					<xsl:when test="price!=''">
						<xsl:value-of select="format-number(price, '#,##0.00')"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:text>/</xsl:text>
					</xsl:otherwise>
				</xsl:choose>
			</td>
		</tr>
	</xsl:template>
</xsl:stylesheet>
