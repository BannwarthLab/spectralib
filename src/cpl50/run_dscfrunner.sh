#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=12
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=2GB
#SBATCH --job-name=0
#SBATCH --output=output.%J.txt
#SBATCH --signal=B:USR1@120

### beginning of executable commands
# Note: the OMP_NUM_THREADS envvar is set automatically - do not overwrite!

your_cleanup_function() {
    echo "Cleanup at $(date)"
        rm $tdir/*tmp*
        mkdir -p $SLURM_SUBMIT_DIR/dump
        cp ./*  $SLURM_SUBMIT_DIR/dump && rm -rf $tdir
}

trap 'your_cleanup_function' USR1 SIGTERM SIGKILL

dir=$(pwd)

tdir=$(mktemp -d $TMPDIR/XXXXXXXXXXXXXXXXXX)

echo 'temporary directory were computations are run:' $tdir 

echo $SLURM_SUBMIT_DIR/$dir
for f in $(ls -r ) ; do
        cp $f $tdir
done

cd $tdir


module load orca/6.1.0
module load xtb/6.7.0
source "/archive/nmaser/documents/venv4/bin/activate"
export XTBEXE=$(which xtb)


# command lines
dscfrunner_main.py coord.xyz --state 1 --tdinp td.inp --guessinp guess.inp --dscfinp dscf.inp --tdoptinp tdopt.inp --tdfallback > outfile.txt &

wait

shopt -s extglob
rm output*
cp -r ./!(*tmp*) $dir && rm -rf $tdir

cd $SLURM_SUBMIT_DIR


