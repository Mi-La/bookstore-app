<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

   <xsl:output method="xml" omit-xml-declaration="no" indent="yes"/>

   <xsl:strip-space elements="*"/>

   <xsl:template match="/orders">

      <xsl:copy>

        <xsl:apply-templates select="order"/>

      </xsl:copy>

   </xsl:template>

   <xsl:template match="order">

        <xsl:variable name="info" select="info/*"/>
        <xsl:for-each select="products/product">
          <product>
            <xsl:copy-of select="$info"/>
            <xsl:copy-of select="*"/>
          </product>
        </xsl:for-each>

   </xsl:template>

 </xsl:stylesheet>
