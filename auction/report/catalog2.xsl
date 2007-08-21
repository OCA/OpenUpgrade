<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">
<!--<xsl:import href="../../custom/corporate_defaults.xsl"/>-->
<xsl:template match="catalog">
<document>
<docinit>
</docinit>
<template>
        <pageTemplate id="first">
                <pageGraphics>
                        <stroke color="(0.6,0.3,0.1)"/>
                        <fill color="(0.6,0.3,0.1)"/>

                        <image x="2cm" y="22cm" width="5cm" height="5cm" file="/home/pmo/Desktop/najjla/images/aeko_logo.jpg"/>
                        <setFont name="Helvetica" size="15"/>
                        <drawCentredString x="14cm" y="25.3cm">BVBA Veilingen AEKO</drawCentredString>
                        <setFont name="Helvetica" size="13"/>
                        <drawCentredString x="14cm" y="24.7cm">Gouverneur Verwilghensingel 18C - B 3500 Hasselt</drawCentredString>
                        <drawCentredString x="14cm" y="24.1cm">Tel: 011/22.04.08 - Fax: 011/23.31.03</drawCentredString>
                        <drawCentredString x="14cm" y="23.5cm">Website: Aeko.be - E-Mail: info@aeko.be</drawCentredString>
                        <drawCentredString x="14cm" y="22.9cm">H.R.HASSELT: 104464</drawCentredString>
                        <fill color="(0.2,0.2,0.2)"/>
                        <stroke color="(0.2,0.2,0.2)"/>
                        <setFont name="Helvetica" size="14"/>
                        <drawCentredString x="105mm" y="4.7cm">Bezoek onze volledige catalogus op www.aeko.be</drawCentredString>

                        <setFont name="Helvetica" size="12"/>
                        <drawCentredString x="105mm" y="3.5cm">Expertise en inname van goederen voor onze volgende veilingen:</drawCentredString>
                        <drawCentredString x="105mm" y="3.0cm">elke woensdag van 10.00 to 12.00 en van 14.00 to 17.00 uur</drawCentredString>
                        <drawCentredString x="105mm" y="2.5cm">en na afspraak op tel. 011.22.04.08</drawCentredString>
                </pageGraphics>
                <frame id="column" x1="2.0cm" y1="6cm" width="18cm" height="16cm"/>
        </pageTemplate>
        <pageTemplate id="others">
                <pageGraphics>
                        <drawRightString x="18.5cm" y="27.2cm"><xsl:value-of select="info"/></drawRightString>
                        <lineMode width="1mm"/>
                        <lines>2.0cm 27cm 19cm 27cm</lines>
                        <setFont name="Helvetica" size="30"/>
                        <drawString x="20mm" y="27.2cm">AEKO</drawString>
                        <fill color="(0.2,0.2,0.2)"/>
                        <stroke color="(0.2,0.2,0.2)"/>
                        <lineMode width="0.5mm"/>
                        <lines>1.5cm 1.8cm 19.5cm 1.8cm</lines>

                        <setFont name="Helvetica" size="12"/>
                        <drawString x="15mm" y="1.2cm">www.aeko.be</drawString>
                        <drawCentredString x="105mm" y="1.2cm">Tel: 011.22.04.08 - Fax: 011.23.31.03</drawCentredString>
                        <drawRightString x="195mm" y="1.2cm">info@aeko.be</drawRightString>
                </pageGraphics>
                <frame id="column" x1="2cm" y1="2.4cm" width="17cm" height="24cm"/>
        </pageTemplate>
</template>
<stylesheet>
        <paraStyle name="slogan" fontName="Helvetica-Bold" fontSize="20" alignment="center"/>
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
        <blockTableStyle id="product">
                <blockValign value="TOP"/>
                <blockAlignment value="CENTER" start="0,0" stop="0,-1"/>
        </blockTableStyle>
        <blockTableStyle id="donation">
                <blockFont name="Helvetica-BoldOblique" size="24" start="0,0" stop="-1,0"/>
                <blockAlignment value="RIGHT" start="-1,0" stop="-1,-1"/>
                <lineStyle kind="LINEBELOW" start="0,0" stop="-1,0"/>
        </blockTableStyle>
</stylesheet>
<story>
        <para style="slogan"><xsl:value-of select="info"/></para>

        <spacer length="0.7cm"/>


        <spacer length="1.0cm"/>

        <blockTable colWidths="5cm,7cm">
        <tr>
                <td>
                        <image height="6cm" width="7cm">
                        <xsl:attribute name="file">
                                <xsl:value-of select="promotion1"/>
                        </xsl:attribute>
                        </image>
                </td>

        </tr>
        </blockTable>



        <setNextTemplate name="others"/>

        <pageBreak/>

        <xsl:apply-templates select="products"/>
</story>
</document>
</xsl:template>

<xsl:template match="product">
        <xsl:if test="newpage">
                <condPageBreak height="20cm"/>
        </xsl:if>

        <xsl:choose>
                <xsl:when test="0">
                        <!-- photo on the left (code in unused at the moment) -->

                        <blockTable style="product" colWidths="5.5cm,11.5cm">
                        <tr>

                                <td>


                                        <para>
                                                <xsl:for-each select="infos/info[position() &gt; 1]">
                                                        <xsl:value-of select="."/>
                                                </xsl:for-each>
                                        </para>

                                        <spacer length="1mm"/>

                                        <xsl:if test="lot_est1&gt;0">
                                                <para>
                                                        <xsl:value-of select="format-number(lot_est1, '#,##0.00')"/> / <xsl:value-of select="format-number(lot_est2, '#,##0.00')"/> Euro
                                                </para>
                                        </xsl:if>
                                </td>
                        </tr>
                        </blockTable>
                </xsl:when>
                <xsl:otherwise>
                        <!-- photo on the right -->

                        <blockTable style="product" colWidths="11.5cm,5.5cm">
                        <tr>
                                <td>

                                        <spacer length="1mm"/>



                                        <xsl:for-each select="infos/info[position() &gt; 1]">
                                                <para>
                                                        <xsl:value-of select="."/>
                                                </para>
                                        </xsl:for-each>

                                        <spacer length="1mm"/>

                                        <xsl:if test="lot_est1&gt;0">
                                                <para>
                                                        <xsl:value-of select="format-number(lot_est1, '#,##0.00')"/> / <xsl:value-of select="format-number(lot_est2, '#,##0.00')"/> Euro
                                                </para>
                                        </xsl:if>
                                </td>

                        </tr>
                        </blockTable>
                </xsl:otherwise>
        </xsl:choose>
</xsl:template>

<xsl:template match="products">
        <xsl:apply-templates select="product"/>
</xsl:template>
</xsl:stylesheet>

