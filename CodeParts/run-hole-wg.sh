#! /bin/bash

MPBFILE=PPWG-mirror.ctl
MPBFILEDIR=../..

print_help ()
{
    echo "Usage:"
    echo "    run-hole-wg.sh [options]"
    echo ""
    echo "Options:"
    echo "  MPB options:"
    echo "    -r <nn>: MPB resolution"
    echo "  Geometry options:"
    echo "    -W <xx.xx>: Beam width (in units of a)"
    echo "    -l <xxx>:   Beam length (in units of a)"
    echo "    -i <xx.xx>: Beam index of refraction"
    echo "    -f <xx.xx>: Filling factor (r/a)"
    echo "    -B <xx.xx>: Background medium refraction index (default is 1.0)"
    echo "    -c <xx.xx>: Width of lattice geometry (in units of a)"
    echo "  Calculation options:"
    echo "    -k <nn>: How many k-points to interpolate."
    echo "    -b <nn>: How many bands to compute."
    echo "    -O <TM|TE>: Polarization (TE is default)"
    echo "Miscellaneous options:"
    echo "    -L <label>: Use <label> as an extra label in the directory name"
    echo "    -D <dir>: Use <dir> as the run directory."
    echo "    -q: Do not plot the fields."
    echo
}

# Default values for the command line arguments.
# Resolution
RES=64

# Number of k-points to interpolate
NKS=16

# Number of bands
NBANDS=3

# Polarization
POL=TE

# Width of the beam in terms of the lattice constant a
WBM=1.0

# Length of the beam in terms of the lattice constant a
LBM=40

# Refractive index of the beam
NBM=2.83

# Filling factor
RROD=0.3

# Background medium refraction index
NBG=1.0

# Width of lattice geometry
CLAD=5.0

# Extra label
XLABEL=

# Run directory (empty means to automatically cocmpute it)
DIRNAME=

# Do plots?
DOPLOT=1

# Root names for the results (FIXME: Add a command line argument for these?)
RESROOT=hole
BANDROOT=hole-bands

# Save command line to a variable.
CMDLINE=`echo $*`

# Process command line arguments.
TEMP=`getopt -o r:f:W:l:i:B:c:k:b:O:L:D:qh -n 'run-rod-wg' -- "$@"`
if [ $? != 0 ] ; then echo "Terminating..." >&2 ; exit 1 ; fi

# Note the quotes around `$TEMP': they are essential!
eval set -- "$TEMP"

while true; do
    case "$1" in
	-r) RES=$2; shift 2;;
	-f) RROD=$2; shift 2;;
	-W) WBM=$2; shift 2;;
        -l) LBM=$2; shift 2;;
	-i) NBM=$2; shift 2;;
	-B) NBG=$2; shift 2;;
	-c) CLAD=$2; shift 2;;
	-k) NKS=$2; shift 2;;
	-b) NBANDS=$2; shift 2;;
	-O) POL=$2; shift 2;;
	-L) XLABEL=$2; shift 2;;
	-D) DIRNAME=$2; shift 2;;
	-q) DOPLOT=0; shift 1;;
	-h) print_help; exit 2;;
	--) shift; break;;
	*) echo "Internal error parsing the command line."; exit 1;;
    esac
done

# Compute the total number of k-points calculated.
NPTS=$((2*${NKS}+3))

# Set variables according to the polarization.
if [ "${POL}" = "TM" ]
then
    lPOL=tm
    lFLD=e
    oFLD=h
else
    lPOL=te
    lFLD=h
    oFLD=e
fi

# Automatically come up with a directory name if none is given.
if [ "${DIRNAME}" = "" ]
then
    # Create the base directory for the run if it does not exist.
    BASEDIR=HO-nbm_${NBM}-wbm_${WBM}-lbm_${LBM}-clad_${CLAD}a
    if [ ! -d ${BASEDIR} ]
    then
        mkdir ${BASEDIR}
    fi
    # Create the single run directory (removing old ones)
    DIRNAME=${BASEDIR}/${RROD}
fi
if [ -d ${DIRNAME} ]
then
    rm -rf ${DIRNAME}.old
    mv ${DIRNAME} ${DIRNAME}.old
fi
mkdir ${DIRNAME}
# And change to it.
cd ${DIRNAME}

# Save the command line
echo $CMDLINE > cmdline.txt

RESFILE=${RESROOT}-r${RROD}.log
BANDFILE=${BANDROOT}-r${RROD}.dat
# Run MPB
mpb rrod=${RROD} nrod=${NBG} pol=${POL} nbm=${NBM} wbm=${WBM} lbm=${LBM} res=${RES} nks=${NKS} clad=${CLAD} nbands=${NBANDS} doplot=${DOPLOT} ${MPBFILEDIR}/${MPBFILE} > $RESFILE
echo -n "#" > $BANDFILE
# Gather the corresponding bands.
if [ "${DOPLOT}" = "1" ]
then
    echo "Gathering results..."
fi
grep ${lPOL}freqs $RESFILE | cut -d"," -f 2,7- --output-delimiter=" " >> ${BANDFILE}
# Once done with it, compress the log file to save space.
bzip2 -9 ${RESFILE}

# If we're not plotting, just exit.
if [ "${DOPLOT}" = "0" ]
then
    rm *.h5   # Erase leftover HDF files...
    exit 0
fi

# ##Process the fields and the dielectric constant data.
echo "Processing the fields..."
mpb-data -x 3 -n 64 -o r${RROD}-epsilon-fixed.h5 r${RROD}-epsilon.h5
rm r${RROD}-epsilon.h5
h5topng r${RROD}-epsilon-fixed.h5

# for i in `seq -f "%02g" 1 ${NBANDS}`
# do
#     mpb-data  -x 1 -n 64 -o r${RROD}-${lFLD}.k${NPTS}.b${i}.z.${lPOL}-fixed.h5 r${RROD}-${lFLD}.k${NPTS}.b${i}.z.${lPOL}yodd.h5 
#     mpb-data  -x 1 -n 64 -o r${RROD}-dpwr.k${NPTS}.b${i}.${lPOL}-fixed.h5 r${RROD}-dpwr.k${NPTS}.b${i}.${lPOL}.h5
#     mpb-data  -x 1 -n 64 -o r${RROD}-${oFLD}.k${NPTS}.b${i}.${lPOL}-fixed.h5 r${RROD}-${oFLD}.k${NPTS}.b${i}.${lPOL}.h5
#     rm r${RROD}-${lFLD}.k${NPTS}.b${i}.z.${lPOL}yodd.h5 r${RROD}-dpwr.k${NPTS}.b${i}.${lPOL}.h5 r${RROD}-${oFLD}.k${NPTS}.b${i}.${lPOL}.h5
#     bzip2 -9 r${RROD}-${oFLD}.k${NPTS}.b${i}.${lPOL}-fixed.h5
# done
# # ##Convert the fields to PNG files
# echo "Plotting fields..."
# for i in 01  # Use the imaginary part for the first band.
# do
#     h5topng -C r${RROD}-epsilon-fixed.h5:data -c bluered -Z -d z.i r${RROD}-${lFLD}.k*.b${i}.z.${lPOL}-fixed.h5
#     h5topng -C r${RROD}-epsilon-fixed.h5:data -c hot -Z -d data r${RROD}-dpwr.k*.b${i}.${lPOL}-fixed.h5
#     bzip2 -9 r${RROD}-${lFLD}.k${NPTS}.b${i}.z.${lPOL}-fixed.h5 r${RROD}-dpwr.k*.b${i}.${lPOL}-fixed.h5
# done
# for i in `seq -f "%02g" 2 ${NBANDS}` # Use the real part for the second and third one.
# do
#     h5topng -C r${RROD}-epsilon-fixed.h5:data -c bluered -Z -d z.r r${RROD}-${lFLD}.k*.b${i}.z.${lPOL}-fixed.h5
#     h5topng -C r${RROD}-epsilon-fixed.h5:data -c hot -Z -d data r${RROD}-dpwr.k*.b${i}.${lPOL}-fixed.h5
#     bzip2 -9 r${RROD}-${lFLD}.k${NPTS}.b${i}.z.${lPOL}-fixed.h5 r${RROD}-dpwr.k*.b${i}.${lPOL}-fixed.h5
# done
# # ##Compress the dielectric constant data.
# bzip2 -9 r${RROD}-epsilon-fixed.h5