<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:phylo="http://www.phyloxml.org"
>
<!--
 trying to convert phyloxml to d3 compatible json
-->

  <xsl:output indent="yes" omit-xml-declaration="yes" method="text" encoding="UTF-8" media-type="text"/>
	
   <xsl:template match="phylo:description" />
   <xsl:template match="phylo:confidence" />
   <xsl:template match="phylo:sequence" />
   <xsl:template match="phylo:events" />
   <xsl:template match="phylo:id" />
   
       
 

   <xsl:template match="//phylo:phylogeny/phylo:name" /> 

   <xsl:template match="phylo:scientific_name" /> 
   


   <!-- object -->
   <xsl:template match="phylo:clade" >
    <xsl:text>{</xsl:text>
    <xsl:if test="not(phylo:taxonomy/phylo:scientific_name)">"name":"null"</xsl:if>
    <xsl:if test="phylo:taxonomy/phylo:scientific_name">
      "name":"<xsl:value-of select="phylo:taxonomy/phylo:scientific_name/text()"/>" 
    </xsl:if>
    <xsl:if test="*[name() = 'clade']">,"children":[</xsl:if>
    
  
    <xsl:apply-templates select="node()"/> 
    <xsl:if test="following-sibling::phylo:clade">},</xsl:if>
    <xsl:if test="not(following-sibling::phylo:clade) and not(parent::phylo:phylogeny)">}]</xsl:if>
    <xsl:if test="not(following-sibling::phylo:clade) and parent::phylo:phylogeny">}</xsl:if>
    <!--<xsl:if test="*[name() = 'clade']">]</xsl:if> --> 
  </xsl:template>

 
  
 
    
</xsl:stylesheet>