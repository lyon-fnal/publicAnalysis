#!/bin/bash
#
#  This is the worker node script for kicker movie (and other magnetic field scans)
#
#  Be sure to submit with --tar_file_name of the tar file with the application
#

# Arguments are
# $1 = arc num
# $2 = output path

set -x

arcnum=$1
outpath=$2

# The fieldTime comes from the PROCESS number 75 + PROCESS * 5
fieldTime=$(expr 75 + $PROCESS \* 5)
echo $fieldTime

date
echo "Starting kickerMovie ${CLUSTER}.${PROCESS}  ${JOBSUBID}"

# We need IFDH
source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups
setup ifdhc v1_6_2 -z /cvmfs/fermilab.opensciencegrid.org/products/common/db

echo "Environment for this job is " > job_env_${CLUSTER}.${PROCESS}.out
env >> job_env_${CLUSTER}.${PROCESS}.out

# Store the jobsub job id
if [ "${PROCESS}" == "0" ]; then
        echo ${JOBSUBJOBID} > ${JOBSUBJOBID}
        ifdh cp -D ${JOBSUBJOBID} $outpath
fi

# Setup g-2 stuff
source /cvmfs/oasis.opensciencegrid.org/gm2/prod/g-2/setup
setup gm2 v6_01_00 -q prof

# Now untar our stuff
tar xvzf $INPUT_TAR_FILE

# Add our local products to the $PRODUCTS directory
export PRODUCTS=$PWD/localProducts_gm2_v6_01_00_prof:$PRODUCTS
echo $PRODUCTS
setup gm2ringsim v3_00_00 -q e7:prof

# Let's see what we've got
ups active

# Now we need to alter the fcl file to add our arcnum and time
csvfile="fieldScan_arc${arcnum}_t${fieldTime}.csv"
vtifile="fieldScan_arc${arcnum}_t_${fieldTime}.vti"
fclfile="kickerMovie_${CLUSTER}_${PROCESS}.fcl"
sed -e "s/%%ARCNUM%%/${arcnum}/" -e "s/%%TIME%%/${fieldTime}/" -e "s/%%CSVFILE%%/${csvfile}/" kickerMovieJob/kickerMovie.fcl_TEMPLATE > $fclfile

# And run!
gm2log="gm2_out_${CLUSTER}.${PROCESS}.log"
gm2 -c $fclfile -n 1 >& $gm2log

# Now convert to vtk
cd kickerMovieJob
tar xvzf paraview.tgz

export PATH=$PATH:$PWD/ParaView-4.3.1-Linux-64bit/bin
cd ..

pvpython kickerMovieJob/convertFieldToImageData.py $csvfile
mv bfield.vti $vtifile

# We want the output root file too
outroot="out_${CLUSTER}.${PROCESS}.root"
mv x.root $outroot

# Copy stuff back
ifdh cp -D $gm2log $vtifile $csvfile $fclfile $outroot $outpath






