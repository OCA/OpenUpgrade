<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">

	<xsl:decimal-format name="MyFormat" NaN="" zero-digit="0" decimal-separator="," grouping-separator="."/>
	
	<xsl:template match="/">
		<xsl:apply-templates select="totals"/>
	</xsl:template>

	<xsl:template match="totals">
		<document xmlns:fo="http://www.w3.org/1999/XSL/Format">
			<template pageSize="21cm,29.7cm">
				<pageTemplate id="first_page">
					<pageGraphics/>

					<frame x1="1.0cm" y1="1.0cm" width="19.0cm" height="27.7cm"/>
				</pageTemplate>
			</template>

			<stylesheet>
				<paraStyle name="title" fontName="Helvetica-Bold" fontSize="16" alignment="center"/>
			 
				<blockTableStyle id="totals">
					<blockFont name="Helvetica-Bold" size="11" start="0,0" stop="-1,0"/>
					<lineStyle kind="LINEBELOW" colorName="black" start="0,0" stop="-1,0"/>
					
					<blockFont name="Helvetica" size="10" start="0,1" stop="-1,-1"/>
					<blockValign value="TOP"/>
					<blockAlignment value="RIGHT" start="3,0" stop="-1,-1"/>
				</blockTableStyle>
			</stylesheet>

			<story>
				<para style="title">Totaux des ventes</para>
							
				<spacer length="1cm"/>
				
				<blockTable colWidths="2.0cm,6.2cm,1.8cm,2.0cm,2.0cm,2.0cm,2.0cm" style="totals">
					<tr>
						<td>N°</td>
						<td>Etude</td>
						<td>Date</td>	
						<td>Adj.</td>	
						<td>Frais</td>
						<td>Total</td>
						<td>Salle</td>
					</tr>
					<xsl:for-each select="dossier">
						<tr>
							<td><xsl:value-of select="num_vignette"/></td>
							<td><para><xsl:value-of select="etude"/></para></td>
							<td><xsl:call-template name="format-date"><xsl:with-param name="date" select="date_reelle"/></xsl:call-template></td>
							<td><xsl:value-of select="format-number(adj, '#.##0,00', 'MyFormat')"/></td>
							<td><xsl:value-of select="format-number(costs, '#.##0,00', 'MyFormat')"/></td>
							<td><xsl:value-of select="format-number(adj+costs, '#.##0,00', 'MyFormat')"/></td>
							<td><xsl:value-of select="format-number(room_costs, '#.##0,00', 'MyFormat')"/></td>
						</tr>
					</xsl:for-each>
				</blockTable>
			</story>
		</document>
	</xsl:template>
	
	<xsl:template name="format-date">
		<xsl:param name="date"/>
		<xsl:variable name="year" select="substring-before($date, '-')"/>
		<xsl:variable name="month" select="substring-before(substring-after($date, '-'), '-')"/>
		<xsl:variable name="day" select="substring-after(substring-after($date, '-'), '-')"/>
		<xsl:value-of select="concat($day, '/', $month, '/', $year)"/>
	</xsl:template>
</xsl:stylesheet>
