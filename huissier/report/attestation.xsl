<?xml version="1.0" encoding="iso-8859-15"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">

	<xsl:decimal-format name="MyFormat" NaN="  " zero-digit="0"/>
	
	<xsl:template match="/">
		<xsl:apply-templates select="lots-list"/>
	</xsl:template>

	<xsl:template match="lots-list">
		<document xmlns:fo="http://www.w3.org/1999/XSL/Format">
			<template pageSize="14.8cm,21cm">
				<pageTemplate id="first_page">
					<pageGraphics>
						<!--logo-->
						<setFont name="Times-Italic" size="11"/>
						<drawCentredString x="4.0cm" y="19.8cm">Maison des Huissiers de Justice</drawCentredString>
						<drawCentredString x="4.0cm" y="19.2cm">de Bruxelles S.C.</drawCentredString>
						<drawCentredString x="4.0cm" y="18.6cm">Huis van de Gerechtsdeurwaarders</drawCentredString>
						<drawCentredString x="4.0cm" y="18.0cm">van Brussel C.V.</drawCentredString>
						
						<setFont name="Helvetica-Bold" size="11"/>
						<drawCentredString x="4.0cm" y="17.0cm">SALLE DE VENTE</drawCentredString>
						<drawCentredString x="4.0cm" y="16.4cm">VERKOOPZAAL</drawCentredString>
						
						<!--page bottom-->
						<setFont name="Times-Italic" size="9"/>
						<drawCentredString x="7.4cm" y="1.3cm">Bruxelles 1000 Brussel, place Anneessensplein, 21/22 - Tél: 02/513.34.47 - Fax: 02/502.42.25</drawCentredString>
						<drawCentredString x="7.4cm" y="0.9cm">E-Mail: maisondeshuissiers-huisdergerechtsdeurwaarders@skynet.be</drawCentredString>
						<drawCentredString x="7.4cm" y="0.5cm">Fortis-B. 210-0594320-53    -    R.C.B - H.R.B 370.982</drawCentredString>

						<lines>0.8cm 1.8cm 14.0cm 1.8cm</lines>
					</pageGraphics>

					<frame id="list" x1="0.8cm" y1="2.0cm" width="13.2cm" height="13.0cm"/>
				</pageTemplate>

				<pageTemplate id="other_pages">
					<pageGraphics>
						<!--page bottom-->
						<setFont name="Times-Italic" size="9"/>
						<drawCentredString x="7.4cm" y="1.3cm">Bruxelles 1000 Brussel, place Anneessensplein, 21/22 - Tél: 02/513.34.47 - Fax: 02/502.42.25</drawCentredString>
						<drawCentredString x="7.4cm" y="0.9cm">E-Mail: maisondeshuissiers-huisdergerechtsdeurwaarders@skynet.be</drawCentredString>
						<drawCentredString x="7.4cm" y="0.5cm">Fortis-B. 210-0594320-53    -    R.C.B - H.R.B 370.982</drawCentredString>

						<lines>0.8cm 1.8cm 14.0cm 1.8cm</lines>
					</pageGraphics>
					
					<frame id="list" x1="0.8cm" y1="2.0cm" width="13.2cm" height="18.0cm"/>
				</pageTemplate>
			</template>

			<stylesheet>
				<paraStyle name="name" fontName="Helvetica-Bold"/>
				<paraStyle name="desc" fontName="Helvetica-Bold"/>
				<paraStyle name="title" fontName="Helvetica-Bold" fontSize="16" alignment="center"/>
			 
				<blockTableStyle id="description">
					<blockFont name="Helvetica-Bold" size="10" start="0,0" stop="-1,0"/>
					<lineStyle kind="LINEBELOW" colorName="black" start="0,0" stop="-1,0"/>
					
					<blockFont name="Helvetica" size="8" start="0,1" stop="-1,-1"/>
					<blockValign value="TOP"/>
					<blockAlignment value="RIGHT" start="2,0" stop="-1,-1"/>
				</blockTableStyle>
				
				<blockTableStyle id="total">
					 <blockValign value="TOP"/>
					 <blockAlignment value="RIGHT"/>
					 <lineStyle kind="LINEABOVE" colorName="black" start="-1,0" stop="-1,0"/>
					 <lineStyle kind="BOX" colorName="black" start="-1,-1" stop="-1,-1"/>
					 <blockBackground colorName="(0.85,0.85,0.85)" start="-1,-1" stop="-1,-1"/>
				</blockTableStyle>
			</stylesheet>

			<story>
				<xsl:for-each select="buyer">
					<setNextTemplate name="other_pages"/>
					<xsl:choose>
						<xsl:when test="lang='nl'">
							<xsl:call-template name="buyer-nl"/>
						</xsl:when>
						<xsl:otherwise>
							<xsl:call-template name="buyer-fr"/>
						</xsl:otherwise>
					</xsl:choose>
					<setNextTemplate name="first_page"/>
					<nextPage/>
				</xsl:for-each>
			</story>
		</document>
	</xsl:template>
	
	<xsl:template name="buyer-fr">
		<para style="title">Attestation d'achat</para>
					
		<spacer length="1cm"/>
		
		<para>Date de la vente: <xsl:call-template name="format-date"><xsl:with-param name="date" select="../date"/></xsl:call-template></para>
		
		<spacer length="0.2cm"/>

		<para>Etude: <xsl:value-of select="../etude/name"/></para>
		<para>Adresse: <xsl:value-of select="../etude/street"/><xsl:text> </xsl:text><xsl:value-of select="../etude/zip"/><xsl:text> </xsl:text><xsl:value-of select="../etude/city"/></para>
		
		<spacer length="0.5cm"/>
		
		<para>Acheteur: <xsl:value-of select="name"/></para>
<!--		
		<para>Adresse: <xsl:value-of select="address"/><xsl:text> </xsl:text><xsl:value-of select="zip"/><xsl:text> </xsl:text><xsl:value-of select="city"/></para>
-->
	
		<spacer length="1.0cm"/>
		
		<blockTable colWidths="1.2cm,12.0cm" style="description">
<!--
		<blockTable colWidths="1.2cm,7.2cm,1.8cm,1.5cm,1.5cm" style="description">
-->		
			<tr>
				<td>N°</td>
				<td>Description</td>
<!--				
				<td>Prix d'adj.</td>	
				<td>Frais</td>
				<td>Total</td>
-->				
			</tr>
			<xsl:apply-templates select="lot"/>
		</blockTable>
		
		<spacer length="0.8cm"/>
	
		<para>Aucun objet ne pourra être enlevé sans ce document.</para>
		
		<spacer length="0.8cm"/>
		
		<para>Attention: Cette attestation ne peut en aucun cas remplacer l'extrait du P.V. de vente judiciaire. Ce dernier ne peut être delivré que par l'huissier de justice instrumentant (art. 15,2° A.R. 30/11/'76).</para>
	</xsl:template>

	<xsl:template name="buyer-nl">
		<para style="title">Aankoop bewijs</para>
					
		<spacer length="1cm"/>
		
		<para>Datum van de verkoop: <xsl:call-template name="format-date"><xsl:with-param name="date" select="../date"/></xsl:call-template></para>
		
		<spacer length="0.2cm"/>
		
		<para>Kantoor: <xsl:value-of select="../etude/name"/></para>
		<para>Adres: <xsl:value-of select="../etude/street"/><xsl:text> </xsl:text><xsl:value-of select="../etude/zip"/><xsl:text> </xsl:text><xsl:value-of select="../etude/city"/></para>
		
		<spacer length="0.5cm"/>
		
		<para>Koper: <xsl:value-of select="name"/></para>
<!--		
		<para>Adres: <xsl:value-of select="address"/><xsl:text> </xsl:text><xsl:value-of select="zip"/><xsl:text> </xsl:text><xsl:value-of select="city"/></para>
-->		
	
		<spacer length="1.0cm"/>

		<blockTable colWidths="1.2cm,12.0cm" style="description">
<!--		
		<blockTable colWidths="1.2cm,7.2cm,1.8cm,1.5cm,1.5cm" style="description">
-->		
			<tr>
				<td>Nr</td>
				<td>Omschrijving</td>
<!--				
				<td>Geboden Prijs</td>	
				<td>Kosten</td>
				<td>Totaal</td>
-->				
			</tr>
			<xsl:apply-templates select="lot"/>
		</blockTable>

		<spacer length="0.8cm"/>
	
		<para>Geen enkele voorwerp kan worden afgehaald zonder dit document.</para>
		
		<spacer length="0.8cm"/>
		
		<para>Opgelet: Dit bewijs vervangt geenszins het uittreksel uit het PV van openbare verkoop, dat alleen door de optredende gerechtsdeurwaarder wordt afgeleverd (art. 15,2° K.B. 30/11/'76).</para>
	</xsl:template>

	<xsl:template match="lot">
		<tr>
			<td><xsl:value-of select="number"/></td>
			<td><para><xsl:value-of select="description"/></para></td>
<!--			
			<td><xsl:value-of select="format-number(adj_price, '#,##0.00', 'MyFormat')"/>€</td>
			<td><xsl:value-of select="format-number(costs, '#,##0.00', 'MyFormat')"/>€</td>
			<td><xsl:value-of select="format-number(costs+adj_price, '#,##0.00', 'MyFormat')"/>€</td>
-->			
		</tr>
	</xsl:template>
	
	<xsl:template name="format-date">
		<xsl:param name="date"/>
		<xsl:variable name="year" select="substring-before($date, '-')"/>
		<xsl:variable name="month" select="substring-before(substring-after($date, '-'), '-')"/>
		<xsl:variable name="day" select="substring-after(substring-after($date, '-'), '-')"/>
		<xsl:value-of select="concat($day, '/', $month, '/', $year)"/>
	</xsl:template>
</xsl:stylesheet>
