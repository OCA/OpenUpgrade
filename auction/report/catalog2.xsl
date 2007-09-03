<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">
<xsl:template match="report">
<document>

<template>
	<pageTemplate id="first">
		<pageGraphics>
			<stroke color="(0.6,0.3,0.1)"/>
			<fill color="(0.6,0.3,0.1)"/>

			<image x="7cm" y="25cm" file="/home/pmo/Desktop/najjla/images/flagey_logo.jpg"/>

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
			<image x="-0.0cm" y="27.3cm" file="/home/pmo/Desktop/najjla/images/flagey_head.png"/>
			<drawRightString x="17.5cm" y="27.6cm">Vente antiquitée mardi 12 juin 07 à 10H</drawRightString>
			<lineMode width="1mm"/>
			<setFont name="Helvetica" size="26"/>
			<!-- <drawString x="10mm" y="27.8cm">Flagey.com</drawString> -->
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
        <paraStyle name="slogan1" fontName="Helvetica-Bold" fontSize="15" alignment="left"/>
         <paraStyle name="slogan2" fontName="Helvetica" fontSize="12"  alignment="left"/>
        <paraStyle name="slogan" fontName="Helvetica-Bold" fontSize="15" alignment="center"/>
        <paraStyle name="footnote" fontName="Helvetica" fontSize="10" alignment="center"/>
        <paraStyle name="note" fontName="Helvetica" fontSize="8" leftIndent="3mm"/>
        <paraStyle name="homehead" fontName="Helvetica" fontSize="12" alignment="center"/>
        <paraStyle name="artist" fontName="Helvetica-Bold"/>
        <paraStyle name="prodtitle" fontName="Helvetica-BoldOblique" fontSize="8"/>
        <blockTableStyle id="infos">
                <blockValign value="TOP"/>
                <blockTopPadding value="0"/>
                <blockBottomPadding value="0"/>
        </blockTableStyle>
        <blockTableStyle id="product1">
                <blockValign value="TOP"/>
                <blockAlignment value="LEFT" start="0,2" stop="0,-5"/>
        </blockTableStyle>
        <blockTableStyle id="donation">
                <blockFont name="Helvetica-BoldOblique" size="24" start="0,0" stop="-1,0"/>
                <blockAlignment value="RIGHT" start="-1,0" stop="-1,-1"/>
                <lineStyle kind="LINEBELOW" start="0,0" stop="-1,0"/>
        </blockTableStyle>
</stylesheet>

	<story>
	<para style="slogan"> Vente antiquitée <xsl:value-of select="catalog/name"/></para>
	<spacer length="1.0cm"/>
	<para style="slogan">le mardi 12 juin 07 à 10H <xsl:value-of select="catalog/AuctionDate1"/> <xsl:value-of select="catalog/AuctionDate2"/></para>

	<spacer length="1.0cm"/>
	<spacer length="0.7cm"/>


<blockTable colWidths="11cm,8cm">

	<tr>-
		<td>

<!--			<para><xsl:value-of select="catalog/promotion1"/></para>-->
			<image height="6cm" width="7cm" >
<!--				<xsl:attribute name="file">-->
					<xsl:value-of select="catalog/promotion1"/>
<!--				</xsl:attribute>-->
			</image>
		</td>
		<td>
			<image height="6cm" width="7cm">
					<xsl:value-of select="catalog/promotion2"/>
			</image>
		</td>
</tr>
</blockTable>
<setNextTemplate name="others"/>
	<pageBreak/>
	<xsl:apply-templates select="catalog/products"/>
</story>
</document>
</xsl:template>


<xsl:template match="products">
			<xsl:apply-templates select="product">
				<xsl:sort order="ascending" data-type="number" select="infos/lot_num"/>
			</xsl:apply-templates>

</xsl:template>

<xsl:template match="product">
<!--        <xsl:if test="newpage">-->
<!--                <condPageBreak height="20cm"/>-->
<!--        </xsl:if>-->

<xsl:choose>
<xsl:when test="string-length(infos/Image) &gt;2">


            <blockTable style="product1" colWidths="4.5cm,4.5cm">

                 <tr>
                     <td>
                       <para style="slogan1">
	                  <xsl:value-of select="infos/lot_num"/>-- <spacer length="0.5mm"/> <xsl:value-of select="infos/info"/>
						</para>
						  <spacer length="6.0mm"/>
		     			   <xsl:if test="lot_est1&gt;0">
				           <para style="slogan2">
				            Max Est <xsl:value-of select="format-number(lot_est1, '#,##0.00')"/>/Min Est<xsl:value-of select="format-number(lot_est2, '#,##0.00')"/> Euro
				            </para>
				       </xsl:if>
					</td>
						<td>
						<image height="3.5cm" width="4.5cm">
									<xsl:value-of select="infos/Image"/>
						</image>
				   </td>
		    </tr>
  </blockTable>
</xsl:when>
<xsl:otherwise>
			<!-- photo on the right-->

       <blockTable style="product1" colWidths="9.0cm">
		       <tr>

		                     <td>
		                       <para style="slogan1">
			                  <xsl:value-of select="infos/lot_num"/>-- <spacer length="0.5mm"/> <xsl:value-of select="infos/info"/>
								</para>
								  <spacer length="8.0mm"/>
				     			   <xsl:if test="lot_est1&gt;0">
						           <para style="slogan2">
						            Max Est <xsl:value-of select="format-number(lot_est1, '#,##0.00')"/>/Min Est<xsl:value-of select="format-number(lot_est2, '#,##0.00')"/> Euro
						            </para>
						       </xsl:if>
							</td>

				  </tr>
  </blockTable>
</xsl:otherwise>
</xsl:choose>

</xsl:template>


</xsl:stylesheet>
