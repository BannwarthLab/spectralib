#!/bin/bash

#solvents=(
#4.7113 4.7113 8.93 
#2.2099 32.613 24.852 24.852 2.228 
#4.7113 4.7113 4.7113
#8.93 4.7113
#4.7113 
#2.228 2.0165
#8.93 8.93 
#2.3741 4.7113 
#8.93
#4.7113 8.93 8.93 8.93 2.3741
#)

solvents=(
chcl3 chcl3 ch2cl2 
dioxane methanol ethanol ethanol ccl4
chcl3 chcl3 chcl3 
ch2cl2 chcl3 
chcl3 
ccl4 cyclohexane 
ch2cl2 ch2cl2 
toluene chcl3 
ch2cl2 
chcl3 ch2cl2 ch2cl2 ch2cl2 toluene
)


mults=(
1 1 1 # 1-3
1 1 1 1 1 #8-12
1 1 1 #13-15
1 1 #20-21
1 #28
2 2 #29-30
1 1 #31-32
1 1 #33-35
1 #38 
1 1 1 1 1 #43,45,47,48,52
)


# Check lengths match
if [ "${#solvents[@]}" -ne "${#mults[@]}" ]; then
    echo "ERROR: solvents and mults have different lengths"
    exit 1
fi


# Explicit molecule IDs to process
ids=(0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25)
for i in "${ids[@]}"
do
    dir=$(printf "%04d" "$i")
    mkdir -p "$dir"

    cp td_template.inp     "$dir/td.inp"
    cp guess_template.inp  "$dir/guess.inp"
    cp dscf_template.inp   "$dir/dscf.inp"
    cp tdopt_template.inp  "$dir/tdopt.inp"
    cp run_dscfrunner.sh   "$dir"

    eps="${solvents[$i]}"
    mult="${mults[$i]}"

    for inp in "$dir"/*.inp
    do
        sed -i \
            -e "s/XXXX/${eps}/g" \
            -e "s/AAAA/${mult}/g" \
            "$inp"
    done

    echo "${dir}  ->  epsilon=${eps}   mult=${mult}"

    cp ../final_geos/"$dir"/coord.xyz $dir



    cd $dir
    
    sed -i "s/QQQQ/${i}/g" run_dscfrunner.sh

    sbatch run_dscfrunner.sh
    cd ..
done
