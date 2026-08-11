module load gromacs

mkdir 6_cmd-1
cd 6_cmd-1
cp ../cmd.mdp .
gmx_mpi grompp -f cmd.mdp -c ../5_npt-10/npt.gro -t ../5_npt-10/npt.cpt -p ../2_md-preparation/gleap.top -n ../2_md-preparation/gleap.ndx -o cmd.tpr -maxwarn 1
gmx_mpi dump -s cmd.tpr > cmd.1.txt

for cnt in {1..5}; do
if [ ! -f cmd$cnt.tpr ]; then
	if [ $cnt -eq 1 ]; then
		gmx_mpi grompp -f cmd.mdp -c ../5_npt-10/npt.gro -t ../5_npt-10/npt.cpt -p ../2_md-preparation/gleap.top -n ../2_md-preparation/gleap.ndx -o cmd$cnt.tpr -maxwarn 1
	else
		gmx_mpi grompp -f cmd.mdp -c cmd$(($cnt-1)).gro -t cmd$(($cnt-1)).cpt -p ../2_md-preparation/gleap.top -n ../2_md-preparation/gleap.ndx -o cmd$cnt.tpr -maxwarn 1
	fi
fi
if [ ! -f cmd$cnt.gro ]; then
	if [ -f cmd$cnt.cpt ]; then 
		gmx_mpi mdrun -deffnm cmd$cnt -cpi cmd$cnt.cpt
	else
		gmx_mpi mdrun -deffnm cmd$cnt 
	fi
fi
echo Pressure | gmx_mpi energy -f cmd$cnt.edr -o Pressure$cnt.xvg
echo Density | gmx_mpi energy -f cmd$cnt.edr -o Density$cnt.xvg
echo Temperature | gmx_mpi energy -f cmd$cnt.edr -o Temperature$cnt.xvg


gmx_mpi trjconv -s cmd$cnt.tpr -f cmd$cnt.gro -n ../2_md-preparation/gleap.ndx -o cmd$cnt.whole.gro -pbc whole <<EOF
System
EOF
gmx_mpi trjconv -s cmd$cnt.tpr -f cmd$cnt.whole.gro -n ../2_md-preparation/gleap.ndx -o cmd$cnt.whole.target.gro <<EOF
Target
EOF

gmx_mpi trjconv -s cmd$cnt.tpr -f cmd$cnt.xtc -n ../2_md-preparation/gleap.ndx -o cmd$cnt.skip10.whole.xtc -skip 10 -pbc whole <<EOF
System
EOF
gmx_mpi trjconv -s cmd$cnt.tpr -f cmd$cnt.skip10.whole.xtc -n ../2_md-preparation/gleap.ndx -o cmd$cnt.skip10.whole.target.xtc <<EOF
Target
EOF

gmx_mpi editconf -f cmd$cnt.gro -o cmd$cnt.pdb
gmx_mpi trjconv -f cmd$cnt.xtc -s cmd$cnt.tpr -n ../2_md-preparation/gleap.ndx -o pbc$cnt.xtc -center -pbc mol <<EOF
Center
Target
EOF

gmx_mpi trjconv -f pbc$cnt.xtc -s cmd$cnt.tpr -o rot_trans_fit$cnt.xtc -fit rot+trans -n ../2_md-preparation/gleap.ndx <<EOF
Target
Target
EOF


done
cd ..


gmx_mpi trjconv -f cmd5.xtc -s cmd5.tpr -n ../2_md-preparation/gleap.ndx -o nopbc.xtc -center -pbc mol. # Center System
gmx_mpi trjconv -f nopbc.xtc -s cmd5.tpr -o rot_trans_fit.xtc -fit rot+trans -n ../2_md-preparation/gleap.ndx.  # Target System