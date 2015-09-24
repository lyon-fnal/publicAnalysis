#!/usr/bin/env pvpython

# Start up ParaView and connect this Jupyter notebook to it.
# This script runs in pvpython (not regular python)

# You can import this into a Jupyter notebook and then,
#   import connectParaViewJuputer as cpvj
#   cpvj.connect()   # the remote connection object will be returned, but you
#                      typically don't need it
#
#  We assume that pvpython is in the $PATH

#
#

import paraview.simple as pv
import paraview.collaboration as pvc

print 'ParaView <--> Jupyter Connection'
print 'Follow these steps:'
print '   1) Start the ParaView server with "pvserver --multi-clients"'
print '   2) Start the ParaView GUI and connect to the server'
print '   3) In pvpython (not regular python) make the connection and take control of the gui with'
print '        c = connectParaViewJuputer.Connection()'

def startParaViewProcesses(paraviewPath):
  # Run pvserver with --multi-clients
  subprocess.Popen(["pvserver", "--multi-clients"])

class Connection:

  def __init__(self, serverPort=11111, serverHost="localhost"):
    """Create a connection with a running pvserver and a running ParaView gui connected to that server.
       Optional arguments are serverPort (default 11111) and serverHost (default localhost)"""
  
  
    self.serverPort = serverPort
    self.serverHost = serverHost
    
    self.rc = None  # The remote connection
    self.cm = None  # Collaboration
  
    self.connectToServer()
    self.takeControl()


  def connectToServer(self):
    
    # Connect
    self.rc = pv.Connect(self.serverHost, self.serverPort)
    print 'Connected to server'
    
  def takeControl(self):

    # Set up collaboration
    self.cm = self.rc.Session.GetCollaborationManager()
    self.cm.UpdateUserInformations()
    myUserId = self.cm.GetUserId()
    self.cm.SetUserLabel(myUserId, "JupyterNotebook")
    self.cm.PromoteToMaster(myUserId)
    self.cm.FollowUser(myUserId)
    print 'Controlling GUI'


# Free helper functions
def showCam():
  renderView1 = pv.GetActiveViewOrCreate('RenderView')
  print 'renderView1.CameraPosition = ', str(renderView1.CameraPosition)
  print 'renderView1.CameraFocalPoint = ', str(renderView1.CameraFocalPoint)
  print 'renderView1.CameraViewUp = ', str(renderView1.CameraViewUp)
  print 'renderView1.CameraParallelScale = ', str(renderView1.CameraParallelScale)
  print 'RenderAllViews()'



if __name__ == '__main__':

  c = Connection()
  time.sleep(60)



