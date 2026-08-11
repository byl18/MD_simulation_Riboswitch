import MDAnalysis as mda
import numpy as np
from pathlib import Path
from MDAnalysis.analysis import align

top = "/gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAH/test_trial/pacs/post_analysis/dissociation_direction/ref_target.pdb"
base = Path("/gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAH/test_trial/pacs/")

outdir = Path("chimerax")
outdir.mkdir(exist_ok=True)

lig_sel = "resname sah SAH"
rna_sel = "not (resname sah SAH)"

ref = mda.Universe(top)

for trial in range(1, 21):
    traj = base / f"trial{trial:03d}/prd.target.trjcat-all.pbc.skip10.xtc"
    if not traj.exists():
        print(f"skip trial{trial:03d}")
        continue
    print(f"processing trial{trial:03d}")
    u = mda.Universe(top, str(traj))
    lig = u.select_atoms(lig_sel)
    rna = u.select_atoms(rna_sel)
    print("lig atoms:", lig.n_atoms, "RNA atoms:", rna.n_atoms)
    if lig.n_atoms == 0:
        print("No ligand selected. Check ligand resname.")
        print(set(u.atoms.resnames))
        continue
    coms = []
    n_frames = len(u.trajectory)
    cut = int(n_frames * 0.95)
    for i, ts in enumerate(u.trajectory):
        if i >= cut:
            break
        # align current frame to the same reference using RNA atoms
        align.alignto(u, ref, select=rna_sel, weights=None)
        # use center_of_geometry to avoid possible ligand mass problems
        coms.append(lig.center_of_geometry())
    coms = np.array(coms)
    np.savetxt(
        outdir / f"SAH_trial{trial:03d}.csv",
        coms,
        delimiter=",",
        header="x,y,z",
        comments=""
    )
    print(f"written SAH_trial{trial:03d}.csv")

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from pathlib import Path
import colorsys

colors=[colorsys.hsv_to_rgb(i/20,0.8,0.9) for i in range(20)]

for trial in range(1,21):
    print(trial)
    csv_file=f"chimerax/SAH_trial{trial:03d}.csv"
    if not Path(csv_file).exists():
        print(f"skip {csv_file}")
        continue
    coords=pd.read_csv(csv_file)[['x','y','z']].values
    selected=[coords[0]]
    threshold=1.0
    for p in coords[1:]:
        if np.linalg.norm(p-selected[-1])>threshold:
            selected.append(p)
    coords=np.array(selected)
    if len(coords)<201:
        print(f"trial{trial:03d} too short")
        continue
    coords_smooth=np.zeros_like(coords)
    for dim in range(3):
        coords_smooth[:,dim]=savgol_filter(coords[:,dim],51,3)
    tail=int(len(coords)*0.75)
    for dim in range(3):
        coords_smooth[tail:,dim]=savgol_filter(
            coords[tail:,dim],
            min(201,len(coords[tail:])//2*2-1),
            3
        )
    dist=np.linalg.norm(np.diff(coords_smooth,axis=0),axis=1)
    s=np.concatenate([[0],np.cumsum(dist)])
    s_new=np.linspace(0,s[-1],800)
    coords_resampled=np.zeros((800,3))
    for dim in range(3):
        coords_resampled[:,dim]=np.interp(s_new,s,coords_smooth[:,dim])
    coords=coords_resampled
    r,g,b=colors[trial-1]
    with open(f"chimerax/SAH_trial{trial:03d}.bild","w") as f:
        f.write(f".color {r:.3f} {g:.3f} {b:.3f}\n")
        for i in range(len(coords)-1):
            x1,y1,z1=coords[i]
            x2,y2,z2=coords[i+1]
            f.write(f".sphere {x1:.3f} {y1:.3f} {z1:.3f} 0.2\n")
            f.write(f".cylinder {x1:.3f} {y1:.3f} {z1:.3f} {x2:.3f} {y2:.3f} {z2:.3f} 0.1\n")
        x,y,z=coords[-1]
        f.write(f".sphere {x:.3f} {y:.3f} {z:.3f} 0.2\n")
    print(f"written SAH_trial{trial:03d}.bild")



