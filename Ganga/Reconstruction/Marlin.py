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
        if not isinstance(libraries, list):
            raise TypeError("Expected list type !")
        
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
        command += "export MARLIN_DLL={0}".format(self.libraries.join(":"))

        # marlin bin        
        command += "Marlin "
        
        if self.gearFile:
            command += '--global.GearFile={0}'.format(self.gearFile)
        
        for k, v in self.replacementOptions:
            command += '--{0}={1} '.format(k, v)
        
        command += self.marlinXml;
        
        # run command
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
        parser.set("Marlin", "MarlinDll", self.libraries.join(":"))
        parser.set("Marlin", "IlcsoftInitScript", self.ilcsoftInitScript)
        
        for k,v in self.replacementOptions:
            parser.set("MarlinReplacementOptions", str(k), str(v))
    
    def runStandalone(self, fileName):
        """
        """
        from GridScript.Ganga.Utilities import CarefulLoader
        
        parser = ConfigParser.ConfigParser()
        parser.read([fileName])
        
        # read marlin config
        self.readConfigFile(parser)
        
        # create and configure grid loader
        loader = CarefulLoader()
        
        try:
            loader.setUploadCommand( parser.get("CarefulLoader", "uploadCommand") )
        except ConfigParser.NoOptionError:
            pass
        
        try:
            loader.setDownloadCommand( parser.get("CarefulLoader", "downloadCommand") )
        except ConfigParser.NoOptionError:
            pass
        
        try:
            loader.setHost( parser.get("CarefulLoader", "lfcHost") )
        except ConfigParser.NoOptionError:
            pass
        
        # Download input files from grid
        try:
            loader.downloadFiles( parser.items("GridInput") )
        except ConfigParser.NoOptionError:
            pass
        
        # run marlin
        self.run()
        
        # Upload output files to grid
        try:
            loader.uploadFiles( parser.items("GridOutput") )
        except ConfigParser.NoOptionError:
            pass
        
        
