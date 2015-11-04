<?xml version="1.0" encoding="ISO-8859-1"?>
<!--Written by Aric Sanders 11/2010-->

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:h="http://www.w3.org/1999/xhtml">
	<xsl:output method='html' version='1.0' encoding='UTF-8' indent='yes'/>
	<xsl:template match="/">
		<html>
		<head>
		<title><xsl:value-of select="//Wafer_Name"/></title>
		</head>
		<body>	
        <xsl:apply-templates/>  
		</body>
		</html>
	</xsl:template>

    <xsl:template match='Wafer_Name'>
    <h1 style='color:black'><xsl:value-of select="."/></h1>
    <xsl:apply-templates select="Process"/> 
    </xsl:template>

<!-- Ordered List, I hope it always maitains the order-->
    <xsl:template match='Process'>
    <hr/>
    <h2><xsl:value-of select="./Process_Name"/></h2>
    <ol >
    <xsl:for-each select="./Step">
    <li>
    <xsl:value-of select="./Step_Description"/>
    <table border='true'>
            <xsl:for-each select="./Step_Parameters/Tuple/@*">
            <xsl:if test=".!=''">
            <tr><td><b><xsl:value-of select="name()"/> :</b> </td><td><xsl:value-of select="."/></td></tr>
            </xsl:if>
            </xsl:for-each>
     </table>
    </li>
    
    </xsl:for-each>
    </ol>
    </xsl:template>
   <xsl:template match='Step'>


    
    <xsl:value-of select="./Step_Description"/>
    <table border='true'>
            <xsl:for-each select="./Step_Parameters/Tuple/@*">
            <xsl:if test=".!=''">
            <tr><td><b><xsl:value-of select="name()"/> :</b> </td><td><xsl:value-of select="."/></td></tr>
            </xsl:if>
            </xsl:for-each>
     </table>
    
    

  
    </xsl:template>
    
</xsl:stylesheet>