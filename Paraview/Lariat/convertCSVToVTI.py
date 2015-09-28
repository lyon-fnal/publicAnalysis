# Make an image data set from a text file. Here the x, y, z spacing is uniform.

# The first line is the attribute data name/type where type is F, I [no strings])
# The second line of the file has the grid dimensions (how many values on each axis)
# The third line has the grid spacing along each axis
# The fourth line is the origin point
# Then the data -- the x variable varies first, then y, then z.

import vtk
import sys, os
import numpy as np
import vtk.util.numpy_support as ns

def getdtypeFromString(s):
  s = s.strip()
  w = s.split('/')
  t = float
  if w[1].lower() == 'i':
    t = int
  return (w[0], t)

def doit(fname):

  f = open(fname, 'r')
  
  # Read in the names and types
  dtypes = [ getdtypeFromString(v) for v in f.readline().split(",") ]

  # Read the dimensions
  dims = [ int(v) for v in f.readline().split(",") ]

  # Read in the spacing
  sp = [ float(v) for v in f.readline().split(",") ]

  # Read in the origin
  minp = [ float(v) for v in f.readline().split(",") ]

  print "Attribute types are: ", dtypes
  print "Dimensions are: ", dims
  print "Grid spacing is: ", sp
  print "Grid origin is: ", minp

  im = vtk.vtkImageData()
  im.SetDimensions(dims)
  im.SetOrigin(minp)
  im.SetSpacing(sp)

  # Read in the data
  d = np.genfromtxt( fname, dtype=dtypes, delimiter=',', autostrip=True, skip_header=4 )
  print d.dtype


  # Process arrays
  skip = 0
  for i, dtype in enumerate(dtypes):
  
    if skip > 0:
      skip -= 1
      continue

    name, t = dtype
    
    # Does it end in 'x'?
    if name[-1].lower() == 'x':
      # Are there two more columns?
      if len(dtypes) > i+2:
        # Do the next two columns end in 'y' and 'z' respectively
        namey = dtypes[i+1][0]
        namez = dtypes[i+1][0]
        if namey[-1].lower() == 'y' and namez[-1].lower() == 'z':

          # We have an xyz vector (assume float)
          print 'Making vector %s %s %s' % (name, namey, namez)
          arrVtk = ns.numpy_to_vtk( d[ [name, namey, namez] ].view( (np.float, 3) ),
                                   1, vtk.VTK_FLOAT )
          arrVtk.SetName(name[:-1])
          im.GetPointData().AddArray(arrVtk)
          skip = 2
          continue

    # We have a scalar
    vtkType = vtk.VTK_FLOAT
    if t == int:
      vtkType = vtk.VTK_INT
    
    print 'Making scalar %s' % name
    arrVtk = ns.numpy_to_vtk( d[name].ravel(), 1, vtkType)
    arrVtk.SetName(name)
    im.GetPointData().AddArray(arrVtk)
      
  # Write it out
  wname = os.path.splitext( os.path.basename(fname))[0] + ".vti"
  print 'Writing %s' % wname
  w = vtk.vtkXMLImageDataWriter()
  w.SetFileName(wname)
  #w.SetDataModeToAscii()
  w.SetInputData(im)
  w.Write()

if __name__ == '__main__':

    # Get the name of the file
    fname = sys.argv[1]

    doit(fname)
