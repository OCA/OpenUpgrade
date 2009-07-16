<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fo="http://www.w3.org/1999/XSL/Format">

	<xsl:template match="/">
		<xsl:call-template name="rml" />
	</xsl:template>

	<xsl:template name="rml">
		<document filename="example.pdf">
            <template pageSize="29.7cm,21cm" title="Test" author="Martin Simon" allowSplitting="20">
                <pageTemplate id="first">
                    <frame id="first"  x1="2.5cm" y1="2.5cm" width="24.7cm" height="17cm"/>
    			</pageTemplate>
			</template>

			<stylesheet>
				<paraStyle name="normal" fontName="Helvetica" fontSize="6" alignment="center" />
				<paraStyle name="normal-title" fontName="Helvetica" fontSize="6" />
				<paraStyle name="title" fontName="Helvetica" fontSize="18" alignment="center" />
				<paraStyle name="date" fontName="Helvetica-Oblique" fontSize="10" textColor="blue" />
				<paraStyle name="glande" textColor="red" fontSize="7" fontName="Helvetica"/>
				<paraStyle name="normal_people" textColor="green" fontSize="7" fontName="Helvetica"/>
				<paraStyle name="esclave" textColor="purple" fontSize="7" fontName="Helvetica"/>
				<blockTableStyle id="month">
					<!--blockAlignment value="CENTER" start="1,0" stop="-1,-1" /-->
					<blockFont name="Helvetica" size="8" start="0,0" stop="-1,1"/>
					<blockFont name="Helvetica" size="6" start="0,2" stop="-2,-2"/>
					<blockFont name="Helvetica-BoldOblique" size="8" start="0,-1" stop="-1,-1"/>
					<lineStyle kind="LINEABOVE" colorName="black" start="0,0" stop="-1,-1" />
					<lineStyle kind="LINEBEFORE" colorName="black" start="0,0" stop="-1,-1"/>
					<lineStyle kind="LINEAFTER" colorName="black" start="-1,0" stop="-1,-1"/>
					<lineStyle kind="LINEBELOW" colorName="black" start="0,-1" stop="-1,-1"/>
					<blockValign value="TOP"/>
				</blockTableStyle>
			</stylesheet>

			<story>
				<xsl:call-template name="story"/>
			</story>
		</document>
	</xsl:template>

	<xsl:template name="story">
		<para style="title" t="1">Order Quantity</para>
		<spacer length="1cm" />
		<blockTable>
			<xsl:attribute name="style">month</xsl:attribute>
			<xsl:attribute name="colWidths"><xsl:value-of select="report/cols" /></xsl:attribute>
			<tr>
                <td><xsl:value-of select="report/date/attribute::month_year" /></td>
				<xsl:for-each select="report/days/day">
					<td>
						<xsl:value-of select="attribute::number" />
					</td>
				</xsl:for-each>
				<td t="1">Total</td>
			</tr>
			<xsl:apply-templates select="report/step"/>
			<xsl:for-each select="report/step">
				<xsl:variable name="id" select="attribute::id"/>
				<tr>
					<td><para><xsl:value-of select="attribute::name"/></para></td>
					<xsl:for-each select="//report/days/day">
					<xsl:variable name="today" select="attribute::number" />
						<td>
							<para>
								<xsl:value-of select="format-number(sum(//step[@id=$id]/time-element[@date=$today]), '##.##')" />
							</para>
						</td>
					</xsl:for-each>
					<td>
					    <para> 
        				    <xsl:value-of select="format-number(sum(//step[@id=$id]/time-element),'##.##')"/>					        
    					</para>
					</td>
				</tr>
			</xsl:for-each>
			<tr>
				<td t="1">Total</td>
				<xsl:for-each select="report/days/day">
					<xsl:variable name="today" select="attribute::number"/>
					<td><xsl:value-of select="format-number(sum(//time-element[@date=$today]),'##.##')"/></td>
				</xsl:for-each>
				<td><xsl:value-of select="format-number(sum(//time-element),'##.##')"/></td>
			</tr>
		</blockTable>
	</xsl:template>
</xsl:stylesheet>
