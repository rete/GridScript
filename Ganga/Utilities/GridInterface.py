import os, sys


class CarefulLoader(object):
    
    def __init__(self):
        """ CarefulLoader class. Utility to download/upload files from grid
            using lfc command line tools
        """
        self.uploadCommand = "/gridgroup/ilc/rete/carefulUpload.sh"
        self.downloadCommand = "/gridgroup/ilc/rete/carefulDownload.sh"
        self.host = "grid-lfc.desy.de"
        
    def setHost(self, host):
        """ Set the lfc host
        """
        self.host = host
    
    def setUploadCommand(self, command):
        """ Set the upload command
        """
        self.uploadCommand = command
        
    def setDownloadCommand(self, command):
        """ Set the download command
        """
        self.downloadCommand = command
        
    def uploadFiles(self, fileDict):
        """ Upload files on grid using lfc tools
        """
        for localFileName,targetLocation in fileDict:
            
            command = "export LFC_HOST={0}; ".format(self.host)
            command += " ".join([self.uploadCommand, localFileName,targetLocation])
            
            ret = os.system( command )
            
            if ret:
                return ret
   
    def downloadFiles(self, fileDict):
        """ Download files from grid using lfc tools
        """
        for localFileName,targetLocation in fileDict:
            command = "export LFC_HOST={0}; ".format(self.host)
            command += " ".join([self.downloadCommand, localFileName,targetLocation])
            
            ret = os.system( command )
            
            if ret:
                return ret
