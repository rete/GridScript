import os, sys

if __name__ == '__main__' :
    from GridScript.Ganga.Reconstruction.Marlin import Marlin
    
    marlin = Marlin()
    marlin.runStandalone(sys.argv[1])
