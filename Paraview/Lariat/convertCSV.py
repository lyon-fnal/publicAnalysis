# Convert a generic CSV file with point data
# The first line must be of the form
# name/type,name/type  where type is i (integer) or f (float)

#
# Try the numpy way

from vtk.numpy_interface import algorithms as algs
from vtk.numpy_interface import dataset_adapter as dsa
import vtk.util.numpy_support as ns

import numpy as np
import vtk

import os.path
import sys

def getdtypeFromString(s):
    w = s.split('/')
    t = float
    if w[1].lower() == 'i':
        t = int
    elif w[1].lower() == 's':
        t = 'S20'   # allow for a 20 character string
    return (w[0], t)

def doit(fname):

    # Read in the first line of the file to get the dtype
    line1 = open(fname, 'r').readline().strip()
    dtypes = [ getdtypeFromString(w) for w in line1.split(",") ]

    print "Read File"
    d = np.genfromtxt(fname, dtype=dtypes, delimiter=',', autostrip=True, skip_header=1)
    print d.dtype

    # Assemble the polydata
    print 'Assemble polydata'

    # We must have points
    coord = algs.make_vector(d["x"], d["y"], d["z"])
    pts = vtk.vtkPoints()
    pts.SetData(dsa.numpyTovtkDataArray(coord, "Points"))
    numPts = pts.GetNumberOfPoints()

    # Make the vtkPolyData
    polyData = vtk.vtkPolyData()
    polyData.SetPoints(pts)     # Add the points
    polyData.Allocate(numPts)   # Add the cells - we want one cell per point so that cell filters (e.g. threshold) work
    for i in xrange(numPts):
      polyData.InsertNextCell(vtk.VTK_VERTEX, 1, [i])

    # Other arrays
    skip = 0

    # Figure out what arrays we have
    for i, dtype in enumerate(dtypes):

        # Do we need to skip this column?
        if skip > 0:
            skip -= 1
            continue

        name, t = dtype

        # Is it a coordinate?
        if name == 'x':
            # Skip it along with y and z
            skip = 2
            continue

        # Does it end in x?
        if name[-1].lower() == 'x':

            # Are there two more columns?
            if len(dtypes) > i+2:

                # Do the others end in y and z?
                namey = dtypes[i+1][0]
                namez = dtypes[i+2][0]
                if namey[-1].lower() == 'y' and namez[-1].lower() == 'z':
                  

                    # We have a xyz array (assume float)
                    print 'Making array %s %s %s' % (name, namey, namez)
                    arrVtk = ns.numpy_to_vtk( d[ [name, namey, namez] ].view( (np.float, 3) ), 1, vtk.VTK_FLOAT )
                    arrVtk.SetName(name[:-1])
                    polyData.GetPointData().AddArray(arrVtk)
                    skip = 2
                    continue
        
        # We can do numbers the numpy way, but not strings
        arrVtk = None
        if t == float or t == int:
        
          # Regular one column array
          vtkType = vtk.VTK_FLOAT
          if t == int:
              vtkType = vtk.VTK_INT
        
          print 'Making array %s' % name
          arrVtk = ns.numpy_to_vtk( d[name].ravel(), 1, vtkType )

        else:  # Strings
          print 'Making array (string) %s' % name
          arrVtk = vtk.vtkStringArray()
          arrVtk.SetNumberOfValues( len( d[name] ) )
          for i, val in enumerate( d[name] ):
            arrVtk.SetValue(i, val)

        # Add the array to the PolyData as point data
        arrVtk.SetName(name)
        polyData.GetPointData().AddArray(arrVtk)

    # Write to file
    wname = os.path.splitext( os.path.basename( fname ) )[0] + ".vtp"
    print 'Writing %s' % wname
    w = vtk.vtkXMLPolyDataWriter()
    w.SetFileName(wname)
    w.SetInputData(polyData)
    #w.SetDataModeToAscii()
    w.Write()

if __name__ == '__main__':
  [ doit(fname) for fname in sys.argv[1:]]
