<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">

<xsl:template match="catalog">
<document>
<docinit>
</docinit>
<template>
	<pageTemplate id="first">
		<pageGraphics>
			<stroke color="(0.6,0.3,0.1)"/>
			<fill color="(0.6,0.3,0.1)"/>

			<image x="7cm" y="25cm" file="//home/pmo/Desktop/najjla/images/flagey_logo.jpg"/>

			<lines>1cm 3.0cm 20cm 3.0cm</lines>
			<setFont name="Helvetica" size="15"/>
			<drawCentredString x="105mm" y="2.2cm">Hotel des ventes Flagey</drawCentredString>
			<setFont name="Helvetica" size="11"/>
			<drawCentredString x="105mm" y="1.6cm">Rue du Nid, 4 - B-1050 Bruxelles - Tel: 02/644.97.67</drawCentredString>
			<drawCentredString x="105mm" y="1.0cm">Web: Flagey.com - Mail: info@flagey.com - Fax: 02.646.32.35</drawCentredString>


			<fill color="(0.2,0.2,0.2)"/>
			<stroke color="(0.2,0.2,0.2)"/>

		</pageGraphics>
		<frame id="column" x1="2.0cm" y1="6cm" width="18cm" height="18cm"/>
	</pageTemplate>
	<pageTemplate id="others">
		<pageGraphics>
			<image x="1cm" y="27.3cm" file="/home/pmo/Desktop/najjla/images/pdfflagey_head.png"/>
			<drawRightString x="19.5cm" y="27.6cm"><xsl:value-of select="info"/></drawRightString>
				<drawRightString x="19.5cm" y="27.6cm"></drawRightString>

			<lineMode width="1mm"/>
			<setFont name="Helvetica" size="26"/>
			<drawString x="10mm" y="27.8cm">Flagey.com</drawString>
			<fill color="(0.2,0.2,0.2)"/>
			<stroke color="#2b24b6"/>
			<lineMode width="0.5mm"/>
			<lines>1cm 1.6cm 20cm 1.6cm</lines>
			<lines>1.0cm 27.3cm 20cm 27.3cm</lines>

			<setFont name="Helvetica" size="12"/>
			<drawString x="10mm" y="1.0cm">www.flagey.com</drawString>
			<drawCentredString x="105mm" y="1.0cm">Tel: 02.644.97.67 - Fax: 02.646.32.35</drawCentredString>
			<drawRightString x="200mm" y="1.0cm">info@flagey.com</drawRightString>
		</pageGraphics>
		<frame id="column" x1="1cm" y1="1.5cm" width="9.4cm" height="25.5cm"/>
		<frame id="column" x1="10.8cm" y1="1.5cm" width="9.4cm" height="25.5cm"/>
	</pageTemplate>
</template>
<stylesheet>
	<paraStyle name="estimate" alignment="right"/>
	<paraStyle name="slogan" fontName="Helvetica-Bold" fontSize="20" leading="1cm" spaceAfter="1cm" alignment="center"/>
	<paraStyle name="footnote" fontName="Helvetica" fontSize="10" alignment="center"/>
	<paraStyle name="note" fontName="Helvetica" fontSize="8" leftIndent="3mm"/>
	<paraStyle name="homehead" fontName="Helvetica" fontSize="12" alignment="center"/>
	<blockTableStyle id="infos">
		<blockValign value="TOP"/>
		<blockTopPadding value="0"/>
		<blockBottomPadding value="0"/>
	</blockTableStyle>
	<blockTableStyle id="product">
		<blockValign value="TOP"/>
		<blockAlignment value="CENTER" start="0,0" stop="0,-1"/>
	</blockTableStyle>
	<blockTableStyle id="donation">
		<blockFont name="Helvetica-BoldOblique" size="24" start="0,0" stop="-1,0"/>
		<blockAlignment value="RIGHT" start="-1,0" stop="-1,-1"/>
		<lineStyle kind="LINEBELOW" start="0,0" stop="-1,0"/>
	</blockTableStyle>
    <paraStyle name="P1" fontName="Times-Bold" fontSize="10.0" leading="13" alignment="CENTER" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="P2" fontName="Times-Roman" fontSize="10.0" leading="13" alignment="JUSTIFY" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="P3" fontName="Times-Bold" fontSize="10.0" leading="13" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="P4" fontName="Times-Roman" alignment="JUSTIFY" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="P5" fontName="Times-Roman" fontSize="10.0" leading="13" alignment="JUSTIFY" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="P6" fontName="Times-Bold" fontSize="10.0" leading="13" alignment="CENTER" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="P7" fontName="Times-Bold" fontSize="10.0" leading="13" alignment="JUSTIFY" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="P8" fontName="Times-Roman" fontSize="10.0" leading="13" alignment="JUSTIFY" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="P9" fontName="Times-Roman" fontSize="10.0" leading="13" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="P10" fontName="Times-Roman" fontSize="12.0" leading="15" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="P11" fontName="Times-Roman" fontSize="12.0" leading="15" alignment="CENTER" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="P12" fontName="Times-Roman" alignment="CENTER" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="Standard" fontName="Times-Roman"/>
    <paraStyle name="Text body" fontName="Times-Roman" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="Heading" fontName="Helvetica" fontSize="14.0" leading="17" spaceBefore="12.0" spaceAfter="6.0"/>
    <paraStyle name="List" fontName="Times-Roman" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="Caption" fontName="Times-Roman" fontSize="12.0" leading="15" spaceBefore="6.0" spaceAfter="6.0"/>
    <paraStyle name="Index" fontName="Times-Roman"/>
</stylesheet>
<story>
<!--	<para style="slogan"><xsl:value-of select="info"/></para>-->
	<spacer length="0.2cm"/>
<!--	<blockTable colWidths="11cm,7cm">-->
<!--	<tr>-->
<!--		<td>-->
<!--			<image height="6.4cm" width="7cm">-->
<!--			<xsl:attribute name="file">-->
<!--				<xsl:value-of select="promotions1"/>-->
<!--			</xsl:attribute>-->
<!--			</image>-->
<!--		</td>-->
<!--		<td>-->
<!--			<image height="6.4cm" width="7cm">-->
<!--			<xsl:attribute name="file">-->
<!--				<xsl:value-of select="promotions2"/>-->
<!--			</xsl:attribute>-->
<!--			</image>-->
<!--		</td>-->
<!--	</tr><tr>-->
<!--		<td>-->
<!--			<image height="6.4cm" width="7cm">-->
<!--			<xsl:attribute name="file">-->
<!--				<xsl:value-of select="promotions3"/>-->
<!--			</xsl:attribute>-->
<!--			</image>-->
<!--		</td>-->
<!--		<td>-->
<!--			<image height="6.4cm" width="7cm">-->
<!--			<xsl:attribute name="file">-->
<!--				<xsl:value-of select="promotions4"/>-->
<!--			</xsl:attribute>-->
<!--			</image>-->
<!--		</td>-->
<!--	</tr>-->
<!--	</blockTable>-->
<!--	<setNextTemplate name="others"/>-->
<!--	<pageBreak/>-->
<!--	<xsl:apply-templates select="products"/>-->
<!--	<pageBreak/>-->
    <para style="P1">CONDITION DE LA VENTE</para>
    <para style="P2">La vente se fait au comptant.</para>
    <para style="P2">Les acheteurs paieront 20% en sus des encheres, TVA comprise outre le droit de suite s'il y a lieu.</para>
    <para style="P2">Aucune reclamation, de quelque nature qu'elle soit, ne sera admise une fois l'adjudication prononcee, meme si elle a pour objet la description du catalogue.</para>
    <para style="P2">En cas de litige les Tribunaux de Bruxelles seront seuls competents.</para>
    <para style="P3">
      <font color="white"> </font>
    </para>
    <para style="P3">INFORMATION AUX ACHETEURS</para>
    <para style="P4">
      <font face="Times-BoldItalic" size="10.0"/>
    </para>
    <para style="P5">
      <font face="Times-BoldItalic">Tous les lots doivent etre enleves pour le vendredi qui suit la vente a 12h au plus tard</font>
      <font face="Times-Roman" size="10.0">; l'Hotel des ventes passe ce delai se reserve le droit d'envoyer la marchandise en garde-meuble au frais de l'acheteur.</font>
    </para>
    <para style="P2">Seuls les cheques certifies sont acceptes pour une livraison immediate, ou cash, bancontact, Mastercard, Visa. En cas de paiement par cheque bancaire non certifie la livraison sera postposee a l'encaissement des montants dus.</para>
    <para style="P2">
      <font color="white"> </font>
    </para>
    <para style="P6">VERKOOPSVOORWARDEN</para>
    <para style="P7">
      <font color="white"> </font>
    </para>
    <para style="P8">De verkoop geschiedt uitsluitend kontant.</para>
    <para style="P8">De Kopers betalen, buiten hun aankoopprijs, 20% voor verkoopkonsten, BTW, bovendien, desgevallend een volgrecht op de getroffen werken.</para>
    <para style="P8">Eenmaal de toewijzing uitgesproken zal geen enkele klacht worden aanvaard, van welke aar ook, zelfs niet indien zij slaat op de beschrijving in de katalogus.</para>
    <para style="P8">In geval van betwisting zijn alleen de rechtbanken van Brussel bevoegd.</para>
    <para style="P8">
      <font color="white"> </font>
    </para>
    <para style="P7">INLICHTINGEN TER ATTENTIE VAN DE KOPERS</para>
    <para style="P7">
      <font color="white"> </font>
    </para>
    <para style="P4">
      <font face="Times-BoldItalic" size="10.0">Alle goederen moeten ten laatste op 21 januari te 12U afgehaald worden. </font>
      <font face="Times-Roman" size="10.0">Slechts betalcheques worden voor een directe levering geaccepteerd.</font>
    </para>
    <para style="P9">In geval van betaling per bankcheque dus geen betaalcheque zal de levering tot de incassering van de verschuldigde bedragen uitgesteld worden ofwel cash, bankontakt, Mastercard, Visa</para>
    <para style="P10">
      <font color="white"> </font>
    </para>
    <para style="P10">
      <font face="Times-Roman">Compte Banque</font>
    </para>
    <para style="Text body"><font face="Times-Roman">Fortis</font> : 210-0830210-39</para>
    <para style="Text body">BIC: GEBABEBB</para>
    <para style="Text body">IBAN: BE13 2100 8302 1039</para>
    <para style="Text body"><font face="Times-Roman">R.C.</font> Bruxelles 551.721</para>
    <para style="Text body">
      <font color="white"> </font>
    </para>
    <para style="P11">Editeur responsable: Michel Pinckaers, rue du Nid 2-4-6, B 1050 Bruxelles</para>
    <para style="P12">
      <font face="Times-Roman" size="12.0">Tous droits reserves, reproduction meme partielle interdite sans autorisation.</font>
    </para>
</story>
</document>
</xsl:template>

<!-- <xsl:template match="product">-->
<!---->
<!--<xsl:choose> -->
<!--<xsl:when test="string-length(photo) &gt;2">-->
<!--<blockTable style="product" colWidths="5.1cm,4.3cm">-->
<!--<tr>-->
<!--	<td>-->
<!--		<para>-->
<!--			<b><xsl:value-of select="ref"/></b>-->
<!--			<xsl:if test="string-length(artist) &gt;2">-->
<!--				<xsl:text> - </xsl:text><b><xsl:value-of select="artist"/></b>-->
<!--			</xsl:if>-->
<!--			<xsl:text> - </xsl:text>-->
<!--			<xsl:for-each select="infos/info">-->
<!--				<xsl:value-of select="."/>-->
<!--			</xsl:for-each>-->
<!--			<spacer length="2mm"/>-->
<!--		</para>-->
<!--		<xsl:if test="est1>0">-->
<!--			<para style="estimate">-->
<!--				<xsl:text>Est. </xsl:text><i><xsl:value-of select="format-number(est1, '#,##0.00')"/> / <xsl:value-of select="format-number(est2, '#,##0.00')"/> Euro</i>-->
<!--			</para>-->
<!--		</xsl:if>-->
<!--	</td>-->
<!--	<td>-->
<!--		<image width="4.2cm">-->
<!--		<xsl:attribute name="file">-->
<!--			<xsl:value-of select="photo"/>-->
<!--		</xsl:attribute>-->
<!--		</image>-->
<!--	</td>-->
<!--</tr>-->
<!--</blockTable>-->
<!--</xsl:when>-->
<!--<xsl:otherwise>-->
<!--<blockTable style="product" colWidths="9.4cm">-->
<!--<tr>-->
<!--	<td>-->
<!--		<para>-->
<!--			<b><xsl:value-of select="ref"/></b>-->
<!--			<xsl:if test="string-length(artist) &gt;2">-->
<!--				<xsl:text> - </xsl:text><b><xsl:value-of select="artist"/></b>-->
<!--			</xsl:if>-->
<!--			<xsl:text> - </xsl:text>-->
<!--			<xsl:for-each select="infos/info">-->
<!--				<xsl:value-of select="."/>-->
<!--			</xsl:for-each>-->
<!--			<spacer length="2mm"/>-->
<!--		</para>-->
<!--		<xsl:if test="est1>0">-->
<!--			<para style="estimate">-->
<!--				<xsl:text>Est. </xsl:text><i><xsl:value-of select="format-number(est1, '#,##0.00')"/> / <xsl:value-of select="format-number(est2, '#,##0.00')"/> Euro</i>-->
<!--			</para>-->
<!--		</xsl:if>-->
<!--	</td>-->
<!--</tr>-->
<!--</blockTable>-->
<!--</xsl:otherwise>-->
<!--</xsl:choose>-->
<!---->
<!--</xsl:template>-->
<!---->
<!--<xsl:template match="products">-->
<!--	<xsl:apply-templates select="product"/>-->
<!--</xsl:template>-->
</xsl:stylesheet>