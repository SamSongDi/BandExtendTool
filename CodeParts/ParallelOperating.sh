#! /bin/bash

# This is used to solve space problem
# convert h5 to png and delete h5 file
MPBFILEDIR=../..

NBM=2.83
WBM=1.5
RROD=0.25

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
    echo "    -e <xx.xx>: Ending Filling factor"
    echo "    -B <xx.xx>: Background medium refraction index (default is 1.0)"
    echo "    -c <xx.xx>: Width of lattice geometry (in units of a)"
    echo "  Calculation options:"
    echo "    -k <nn>: How many k-points to interpolate."
    echo "    -b <nn>: How many bands to compute."
    echo "    -O <fa|TE>: Polarization (TE is default)"
    echo "Miscellaneous options:"
    echo "    -L <label>: Use <label> as an extra label in the directory name"
    echo "    -D <dir>: Use <dir> as the run directory."
    echo "    -q: Do not plot the fields."
    echo "    -m <nn> number of mirror"
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
WBM=1.5

# Length of the beam in terms of the lattice constant a
LBM=40

# Refractive index of the beam
NBM=2.83

# Filling factor
RROD=0.25

#Ending Filling factor
REND=0.2

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


# Number of mirror in a cell calculated

MIR=15

# Process command line arguments.
TEMP=`getopt -o r:f:e:W:l:i:B:c:k:b:m:O:L:D:q:h -n 'run-rod-wg' -- "$@"`
if [ $? != 0 ] ; then echo "Terminating..." >&2 ; exit 1 ; fi

# Note the quotes around `$TEMP': they are essential!
eval set -- "$TEMP"

while true; do
    case "$1" in
    -r) RES=$2; shift 2;;
    -f) RROD=$2; shift 2;;
    -e) REND=$2; shift 2;;
    -W) WBM=$2; shift 2;;
    -l) LBM=$2; shift 2;;
    -i) NBM=$2; shift 2;;
    -B) NBG=$2; shift 2;;
    -c) CLAD=$2; shift 2;;
    -k) NKS=$2; shift 2;;
    -b) NBANDS=$2; shift 2;;
    -m) MIR=$2; shift 2;;
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
NPTS=$((${NKS}+2))

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

NHOLE=41



BASEDIR=HO-nbm_${NBM}-wbm_${WBM}
DIRNAME=${BASEDIR}/${RROD}
cd ${DIRNAME}

while [ ! -f r${RROD}-epsilon.h5 ]
do
    echo "Waiting..."
    echo r${RROD}-epsilon.h5
    sleep 1
    du -h
done

mpb-data -x 1 -n 64 -o r${RROD}-epsilon-fixed.h5 r${RROD}-epsilon.h5
rm r${RROD}-epsilon.h5

for kpt in `seq -f "%02g" 01 35`
do
    for i in 01  # Use the imaginary part for the first band.
    do
        while [ ! -f r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd.h5 ]
        do
            echo "Waiting..."
            echo r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd.h5 
            sleep 1
            du -h
        done
        mpb-data  -x 1 -n 64 -o r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd-fixed.h5 r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd.h5
        rm r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd.h5
        h5topng -C r${RROD}-epsilon-fixed.h5:data -c bluered -Z -d z.i r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd-fixed.h5
        rm r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd-fixed.h5 
    done
    for i in `seq -f "%02g" 02 ${NBANDS}` # Use the real part for the second and third one.
    do
        while [ ! -f r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd.h5 ]
        do
            echo "Waiting..."
            echo r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd.h5 
            sleep 1
            du -h
        done
        mpb-data  -x 1 -n 64 -o r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd-fixed.h5 r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd.h5
        rm r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd.h5
        h5topng -C r${RROD}-epsilon-fixed.h5:data -c bluered -Z -d z.r r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd-fixed.h5
        rm r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd-fixed.h5 
    done
    for i in 01  # Use the imaginary part for the first band.
    do
        while [ ! -f r${RROD}-${oFLD}.k${kpt}.b${i}.${lPOL}yodd.h5 ]
        do
            echo "Waiting..."
            echo r${RROD}-${oFLD}.k${kpt}.b${i}.${lPOL}yodd.h5
            sleep 1
            du -h
        done
        mpb-data  -x 1 -n 64 -o r${RROD}-${oFLD}.k${NPTS}.b${i}.${lPOL}yodd-fixed.h5 r${RROD}-${oFLD}.k${kpt}.b${i}.${lPOL}yodd.h5
        rm r${RROD}-${oFLD}.k${kpt}.b${i}.${lPOL}yodd.h5
        rm r${RROD}-${oFLD}.k${kpt}.b${i}.${lPOL}yodd-fixed.h5
    done
    for i in `seq -f "%02g" 02 ${NBANDS}` # Use the real part for the second and third one.
    do
        while [ ! -f r${RROD}-${oFLD}.k${kpt}.b${i}.${lPOL}yodd.h5 ]
        do
            echo "Waiting..."
            echo r${RROD}-${oFLD}.k${kpt}.b${i}.${lPOL}yodd.h5
            sleep 1
            du -h
        done
        mpb-data  -x 1 -n 64 -o r${RROD}-${oFLD}.k${NPTS}.b${i}.${lPOL}yodd-fixed.h5 r${RROD}-${oFLD}.k${kpt}.b${i}.${lPOL}yodd.h5
        rm r${RROD}-${oFLD}.k${kpt}.b${i}.${lPOL}yodd.h5
        
        rm r${RROD}-${oFLD}.k${kpt}.b${i}.${lPOL}yodd-fixed.h5
    done

    for i in 01  # Use the imaginary part for the first band.
    do
        while [ ! -f r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd.h5 ]
        do
            echo "Waiting..."
            echo r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd.h5
            sleep 1
            du -h
        done
        mpb-data  -x 1 -n 64 -o r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd-fixed.h5 r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd.h5
        rm r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd.h5
        h5topng -C r${RROD}-epsilon-fixed.h5:data -c hot -Z -d data r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd-fixed.h5
        # h5topng -C r${RROD}-epsilon-fixed.h5:data -c bluered -Z -d z.i r${RROD}-${oFLD}.k${NPTS}.b${i}.${lPOL}yodd-fixed.h5
        # h5topng -C r${RROD}-epsilon-fixed.h5:data -c hot -Z -d data r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd-fixed.h5
        rm r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd-fixed.h5
        # bzip2 -9 r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd-fixed.h5 
        # bzip2 r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd-fixed.h5
    done
    for i in `seq -f "%02g" 02 ${NBANDS}` # Use the real part for the second and third one.
    do
        while [ ! -f r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd.h5 ]
        do
            echo "Waiting..."
            echo r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd.h5
            sleep 1
            du -h
        done
        mpb-data  -x 1 -n 64 -o r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd-fixed.h5 r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd.h5
        rm r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd.h5
        # h5topng -C r${RROD}-epsilon-fixed.h5:data -c bluered -Z -d z.r r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd-fixed.h5
        h5topng -C r${RROD}-epsilon-fixed.h5:data -c hot -Z -d data r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd-fixed.h5
        rm r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd-fixed.h5
        # bzip2 -9 r${RROD}-${lFLD}.k${kpt}.b${i}.z.${lPOL}yodd-fixed.h5
        # bzip2 r${RROD}-dpwr.k${kpt}.b${i}.${lPOL}yodd-fixed.h5
    done

done

rm r${RROD}-epsilon-fixed.h5