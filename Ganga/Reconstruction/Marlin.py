#!/usr/bin/python
import ConfigParser
import os, sys


class Marlin(object):
    
    def __init__(self):
        """ Marlin class constructor
        """
        self.marlinXml = ""
        self.gearFile = ""
        self.replacementOptions = {}
        self.libraries = []
        self.ilcsoftInitScript = ""
        
    def setMarlinXML(self, xml):
        """ Set the marlin xml file
        """
        self.marlinXml = xml
    
    def setGearFile(self, gearFile):
        """ Set the gear file
        """
        self.gearFile = gearFile
    
    def setLibraries(self, libraries):
        """ Set the marlin dll libraries
        """
        self.libraries = libraries
    
    def addLibrary(self, library):
        """ Add a marlin library
        """
        self.libraries.append(library)
        
    def setReplacementOption(self, processorOption, value):
        """ Add replacement processor option.
            Replace it if already exists
        """
        self.replacementOptions[processorOption] = value
    
    def setReplacementOptions(self, items):
        """ Set the processor options to replace 
            using the Marlin command line tool
        """
        self.replacementOptions.clear()
        
        for k, v in items:
            self.replacementOptions[k] = v
    
    def setIlcsoftInitScript(self, script):
        """ Set the init_ilcsoft.sh to source before running marlin
        """
        self.ilcsoftInitScript = script
    
    def run(self):
        """ Run the Marlin command.
            Replace processor options if specified. 
        """
        if not self.marlinXml:
            raise RuntimeError('Marlin XML file not set !')
        
        # source ilsoft
        command = "source {0}; ".format(self.ilcsoftInitScript)
        
        # export marlin dlls
        command += "export MARLIN_DLL={0}; ".format(":".join(self.libraries))

        # marlin bin        
        command += "Marlin "
        
        if self.gearFile:
            command += '--global.GearXMLFile={0} '.format(self.gearFile)
        
        for k, v in self.replacementOptions.items():
            command += '--{0}={1} '.format(k, v)
        
        command += self.marlinXml;
        
        # run command
        print "Running : '" + command + "'"
        return os.system(command)
    
    def readConfigFile(self, parser):
        """ Read config from a parser (ConfigParser).
            Replace all found attributes
        """
        
        self.setReplacementOptions(parser.items("MarlinReplacementOptions"))
        
        try:
            self.marlinXml = parser.get("Marlin", "MarlinXml")
        except ConfigParser.NoOptionError:
            pass
        
        try:
            self.gearFile = parser.get("Marlin", "GearFile")
        except ConfigParser.NoOptionError:
            pass
        
        try:
            self.ilcsoftInitScript = parser.get("Marlin", "IlcsoftInitScript")
        except ConfigParser.NoOptionError:
            pass
        
        try:
            self.libraries = parser.get("Marlin", "MarlinDll").split(":")
        except ConfigParser.NoOptionError:
            pass
        
    def writeConfigFile(self, parser):
        """ Write marlin instancein config parser
            Override parser sections or create if doesn't exists
        """
        if not parser.has_section("Marlin"):
            parser.add_section("Marlin")
            
        if not parser.has_section("MarlinReplacementOptions"):
            parser.add_section("MarlinReplacementOptions")

        parser.set("Marlin", "MarlinXml", self.marlinXml)
        parser.set("Marlin", "GearFile", self.gearFile)
        parser.set("Marlin", "MarlinDll", ":".join(self.libraries))
        parser.set("Marlin", "IlcsoftInitScript", self.ilcsoftInitScript)
        
        for k,v in self.replacementOptions.items():
            parser.set("MarlinReplacementOptions", k, v)
    
    def runStandalone(self, fileName):
        """
        """
        from GridScript.Ganga.Utilities.GridInterface import CarefulLoader
        
        parser = ConfigParser.ConfigParser()
        parser.optionxform=str
        parser.read([fileName])
        
        # read marlin config
        self.readConfigFile(parser)
        
        # create and configure grid loader
        loader = CarefulLoader()
        
        try:
            loader.setUploadCommand( parser.get("GridInput", "uploadCommand") )
        except ConfigParser.NoOptionError, ConfigParser.NoSectionError:
            pass
        
        try:
            loader.setDownloadCommand( parser.get("GridOutput", "downloadCommand") )
        except ConfigParser.NoOptionError, ConfigParser.NoSectionError:
            pass
        
        try:
            loader.setHost( parser.get("GridInput", "lfcHost") )
        except ConfigParser.NoOptionError, ConfigParser.NoSectionError:
            pass
        
        # Download input files from grid
        try:
            loader.downloadFiles( parser.items("GridInput") )
        except ConfigParser.NoOptionError, ConfigParser.NoSectionError:
            pass
        
        # run marlin
        self.run()
        
        try:
            loader.setHost( parser.get("GridOutput", "lfcHost") )
        except ConfigParser.NoOptionError, ConfigParser.NoSectionError:
            pass

        # Upload output files to grid
        try:
            loader.uploadFiles( parser.items("GridOutput") )
        except ConfigParser.NoOptionError, ConfigParser.NoSectionError:
            pass
        
        
