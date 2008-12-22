<?xml version="1.0" encoding="iso-8859-1"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">

	<xsl:decimal-format name="MyFormat" NaN="" zero-digit="0" decimal-separator="," grouping-separator="."/>
	
	<xsl:variable name="initial_bottom_pos">21.8</xsl:variable>
	<xsl:variable name="initial_left_pos">0.4</xsl:variable>
	<xsl:variable name="height_increment">7</xsl:variable>
	<xsl:variable name="width_increment">10.5</xsl:variable>
	<xsl:variable name="frame_height">6.8cm</xsl:variable>
	<xsl:variable name="frame_width">9.9cm</xsl:variable>
	<xsl:variable name="number_columns">2</xsl:variable>
	<xsl:variable name="number_frames">8</xsl:variable>

	<xsl:template match="/">
		<xsl:apply-templates select="vignette-ranges"/>
	</xsl:template>

	<xsl:template match="vignette-ranges">
		<document xmlns:fo="http://www.w3.org/1999/XSL/Format">
			<template leftMargin="2.0cm" rightMargin="2.0cm" topMargin="2.0cm" bottomMargin="2.0cm">
				<pageTemplate id="all">
					<pageGraphics/>
					<xsl:call-template name="vignette-frame">
						<xsl:with-param name="number">0</xsl:with-param>
					</xsl:call-template>
				</pageTemplate>
			</template>

			<stylesheet>
				<paraStyle name="salle" fontName="Helvetica" fontSize="7"/>
				<paraStyle name="price" fontName="Helvetica" fontSize="10"/>
				<paraStyle name="number" fontName="Helvetica-Bold" fontSize="11" alignment="RIGHT"/>

				<blockTableStyle id="num_and_price">
					<blockAlignment value="RIGHT"/>
					<lineStyle kind="BOX" thickness="0.5" colorName="black" start="0,0" stop="0,0"/>
				</blockTableStyle>

				<blockTableStyle id="affaire">
					<blockValign value="TOP"/>
					<blockAlignment value="LEFT"/>
					<blockFont name="Helvetica" size="6"/>
					<lineStyle kind="GRID" thickness="0.5" colorName="black" start="0,0" stop="-1,-1"/>
				</blockTableStyle>
			</stylesheet>

			<story>
				<xsl:apply-templates select="vignette-range">
					<xsl:sort select="first" data-type="number"/>
				</xsl:apply-templates>
			</story>
		</document>
	</xsl:template>
	
	<xsl:template name="vignette-frame">
		<xsl:param name="number" />
		<frame>
			<xsl:attribute name="width">
				<xsl:value-of select="$frame_width"/>
			</xsl:attribute>
			<xsl:attribute name="height">
				<xsl:value-of select="$frame_height"/>
			</xsl:attribute>
			<xsl:attribute name="x1">
				<xsl:value-of select="$initial_left_pos + ($number mod $number_columns) * $width_increment"/>
				<xsl:text>cm</xsl:text>
			</xsl:attribute>
			<xsl:attribute name="y1">
				<xsl:value-of select="$initial_bottom_pos - floor($number div $number_columns) * $height_increment"/>
				<xsl:text>cm</xsl:text>
			</xsl:attribute>
		</frame>

		<xsl:if test="number($number) &lt; $number_frames - 1">
			<xsl:call-template name="vignette-frame">
				<xsl:with-param name="number" select="$number + 1"/>
			</xsl:call-template>
		</xsl:if>
	</xsl:template>
	
	<xsl:template match="vignette-range">
<!--	
		<para>First: <xsl:value-of select="number(first)"/></para>
		<para>Last: <xsl:value-of select="number(last)"/></para>
		<para>Start: <xsl:value-of select="//start"/></para>
		<para>Stop: <xsl:value-of select="//stop"/></para>
-->		
		<xsl:variable name="first">
			<xsl:choose>
				<xsl:when test="//start=''">
					<xsl:value-of select="number(first)"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:choose>
						<xsl:when test="number(first) &gt;= number(//start)">
							<xsl:value-of select="number(first)"/>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="number(//start)"/>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		
		<xsl:variable name="last">
			<xsl:choose>
				<xsl:when test="//stop = ''">
					<xsl:value-of select="number(last)"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:choose>
						<xsl:when test="number(last) &lt;= number(//stop)">
							<xsl:value-of select="number(last)"/>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="number(//stop)"/>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
<!--
		<para>$First: <xsl:value-of select="$first"/></para>
		<para>$Last: <xsl:value-of select="$last"/></para>
-->
		<xsl:call-template name="vignette">
			<xsl:with-param name="number" select="number($first)"/>
			<xsl:with-param name="last" select="number($last)"/>
			<xsl:with-param name="price" select="price"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template name="vignette">
		<xsl:param name="number">0</xsl:param>
		<xsl:param name="last">0</xsl:param>
		<xsl:param name="price">0</xsl:param>
		<para>Volet à apposer sur le PV de placard</para>
		<para>Strook aan te brengen op het PV van de aanplakking</para>
		
		<spacer length="2mm"/>
		
		<blockTable colWidths="4.9cm,4.9cm" style="num_and_price">
			<tr><td><para style="number"><xsl:value-of select="$number"/></para></td><td><para style="price">Prix/Prijs: EUR <xsl:value-of select="format-number($price, '#.##0,00', 'MyFormat')"/></para></td></tr>
			<tr>
				<td><para style="salle">SALLE DE VENTE DES HUISSIERS DE JUSTICE DE BRUXELLES</para></td>
				<td><para style="salle">VERKOOPZAAL VAN DE GERECHTS-</para><para style="salle">DEURWAARDERS BRUSSEL</para></td>
			</tr>
		</blockTable>
		
		<blockTable colWidths="9.8cm" rowHeights="1.3cm,1.3cm" style="affaire">
			<tr><td>Affaire/Zaak:</td></tr>
			<tr><td>contre/tegen:</td></tr>
		</blockTable>
		
		<spacer length="2mm"/>
		
		<para>Date de la vente __________________ Datum van de verkoop</para>

		<nextFrame/>
		
		<para>Volet à apposer sur le placard à afficher à la salle - Strook aan te </para>
		<para>brengen op de plakbrief die in de verkoopzaal moet aangeplakt</para>

		<spacer length="2mm"/>
		
		<blockTable colWidths="4.9cm,4.9cm" style="num_and_price">
			<tr><td><para style="number"><xsl:value-of select="$number"/></para></td><td><para style="price">Prix/Prijs: EUR <xsl:value-of select="format-number($price, '#.##0,00', 'MyFormat')"/></para></td></tr>
			<tr>
				<td><para style="salle">SALLE DE VENTE DES HUISSIERS DE JUSTICE DE BRUXELLES</para></td>
				<td><para style="salle">VERKOOPZAAL VAN DE GERECHTS-</para><para style="salle">DEURWAARDERS BRUSSEL</para></td>
			</tr>
		</blockTable>
		
		<blockTable colWidths="9.8cm" rowHeights="1.3cm,1.3cm" style="affaire">
			<tr><td>Affaire/Zaak:</td></tr>
			<tr><td>contre/tegen:</td></tr>
		</blockTable>
		
		<spacer length="2mm"/>
		
		<para>Date de la vente __________________ Datum van de verkoop</para>

		<nextFrame/>
		
		<xsl:if test="number($number) &lt; number($last)">
			<xsl:call-template name="vignette">
				<xsl:with-param name="number" select="$number + 1"/>
				<xsl:with-param name="last" select="$last"/>
				<xsl:with-param name="price" select="$price"/>
			</xsl:call-template>
		</xsl:if>
	</xsl:template>
</xsl:stylesheet>
