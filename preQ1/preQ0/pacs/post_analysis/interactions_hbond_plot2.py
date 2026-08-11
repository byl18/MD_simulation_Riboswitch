# <<< MODIFIED: compare PreQ0 and PreQ1 in the same residue-wise figures
import os
import pickle
from scipy.stats import mannwhitneyu
import numpy as np
import matplotlib.pyplot as plt
import mdtraj as md

# <<< MODIFIED: set paths for two systems
systems = {
    "PreQ0": {
        "color": "red",
        "top": "/gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/PreQ0/trial01/2_md-preparation/gleap.target.gro",
        "pickle_dir": "/gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/PreQ0/trial01/pacs2/post_analysis/pickle-cache/interactions_hbond",
    },
    "PreQ1": {
        "color": "blue",
        "top": "/gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/PreQ1/trial01/2_md-preparation/gleap.target.gro",
        "pickle_dir": "/gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/PreQ1/trial01/pacs2/post_analysis/pickle-cache/interactions_hbond",
    },
}

n_trials = 20
n_bins = 120
ymax_line = 5.5

os.makedirs("./figures/residue_hbond_compare", exist_ok=True)


# <<< MODIFIED: function to load PaCS-MD interaction results for one system
def load_pacs_interactions(system_info):
    gleap_target = md.load(system_info["top"])
    atom_indices_ligand = gleap_target.topology.select("resid 33")
    atom_indices_rna = gleap_target.topology.select("resid 0 to 32")
    atom_index_ligand_min = min(atom_indices_ligand)

    pickle_dir = system_info["pickle_dir"]

    pacs_interactions = np.zeros(
        (n_trials, len(atom_indices_ligand), len(atom_indices_rna), n_bins)
    )
    pacs_com_distances_bincount = np.zeros((n_trials, n_bins))

    for trial in range(n_trials):
        nonzero_indices, nonzero_values = pickle.load(
            open(f"{pickle_dir}/pacs_interactions_{trial}.pickle", "rb")
        )
        pacs_interactions[trial][nonzero_indices] = nonzero_values

        pacs_com_distances_bincount[trial] = pickle.load(
            open(f"{pickle_dir}/pacs_com_distances_bincount_{trial}.pickle", "rb")
        )

    # <<< MODIFIED: safe normalization to avoid division by zero
    pacs_interactions = np.divide(
        pacs_interactions,
        pacs_com_distances_bincount[:, np.newaxis, np.newaxis, :],
        out=np.zeros_like(pacs_interactions),
        where=pacs_com_distances_bincount[:, np.newaxis, np.newaxis, :] != 0,
    )

    return gleap_target, atom_indices_ligand, atom_index_ligand_min, pacs_interactions


# <<< MODIFIED: load PreQ0 and PreQ1 data
loaded = {}
for name, info in systems.items():
    loaded[name] = {}
    (
        loaded[name]["top"],
        loaded[name]["atom_indices_ligand"],
        loaded[name]["atom_index_ligand_min"],
        loaded[name]["pacs_interactions"],
    ) = load_pacs_interactions(info)


# use PreQ0 topology as reference for RNA residue names
ref_top = loaded["PreQ0"]["top"]

# <<< MODIFIED: plot one figure for each RNA residue
for residue_index_rna in range(33):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), gridspec_kw={"width_ratios": [3, 1]})
    ax_line, ax_box = axes

    residue = ref_top.topology.residue(residue_index_rna)
    line_ymax = 0 
    box_data = []
    box_labels = []
    box_colors = []

    for system_name, system_info in systems.items():
        color = system_info["color"]

        gleap_target = loaded[system_name]["top"]
        atom_indices_ligand = loaded[system_name]["atom_indices_ligand"]
        atom_index_ligand_min = loaded[system_name]["atom_index_ligand_min"]
        pacs_interactions = loaded[system_name]["pacs_interactions"]

        atom_indices_rna_residue = gleap_target.topology.select(f"resid {residue_index_rna}")

        trial_values = []

        for trial in range(n_trials):
            # interaction summed over ligand atoms and all atoms of this RNA residue
            residue_interaction = pacs_interactions[
                trial, :, atom_indices_rna_residue, :
            ].sum(axis=(0, 1))

            residue_interaction = residue_interaction[:40]
            line_ymax = max(line_ymax, np.nanmax(residue_interaction)) 
            # <<< MODIFIED: plot each trial as one line
            ax_line.plot(
                residue_interaction,
                color=color,
                alpha=0.25,
                linewidth=2.0,
            )

            # <<< MODIFIED: one value per trial for boxplot
            # here using mean interaction over dissociation coordinate
            trial_values.append(np.nanmean(residue_interaction))

        box_data.append(trial_values)
        box_labels.append(system_name)
        box_colors.append(color)

    ax_line.set_title(f"{residue} hydrogen-bond changes")
    ax_line.set_xlabel("Ligand–RNA distance bin")
    ax_line.set_ylabel("H-bond frequency")
    ylim_top = line_ymax * 1.2
    if ylim_top == 0:
        ylim_top = 0.1
    ax_line.set_xlim(0, 40)
    ax_line.set_ylim(0, ylim_top)


    # <<< MODIFIED: add legend manually
    ax_line.plot([], [], color="red", label="PreQ0")
    ax_line.plot([], [], color="blue", label="PreQ1")
    ax_line.legend(frameon=False)

    # <<< MODIFIED: boxplot, each trial as one data point
    bp = ax_box.boxplot(
        box_data,
        labels=box_labels,
        patch_artist=True,
        showfliers=False,
    )

    for patch, color in zip(bp["boxes"], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.25)

    for i, (values, color) in enumerate(zip(box_data, box_colors), start=1):
        x = np.random.normal(i, 0.04, size=len(values))
        ax_box.scatter(
            x,
            values,
            color=color,
            alpha=0.7,
            s=25,
            edgecolor="black",
            linewidth=0.3,
        )

    # <<< MODIFIED: Mann–Whitney U-test between PreQ0 and PreQ1
    u_stat, p_value = mannwhitneyu(
        box_data[0],
        box_data[1],
        alternative="two-sided"
    )

    if p_value < 0.0001:
        sig_label = "****"
    elif p_value < 0.001:
        sig_label = "***"
    elif p_value < 0.01:
        sig_label = "**"
    elif p_value < 0.1:
        sig_label = "*"
    else:
        sig_label = None

    # <<< MODIFIED: add significance mark only when p < 0.01
    if sig_label is not None:
        y_box_max = max(np.nanmax(box_data[0]), np.nanmax(box_data[1]))
        h = y_box_max * 0.08
        if h == 0:
            h = 0.02

        x1, x2 = 1, 2
        y = y_box_max + h

        ax_box.plot(
            [x1, x1, x2, x2],
            [y, y + h, y + h, y],
            color="black",
            linewidth=1.2,
        )

        ax_box.text(
            (x1 + x2) / 2,
            y + h,
            sig_label,
            ha="center",
            va="bottom",
            fontsize=14,
            fontweight="bold",
        )

        ax_box.set_ylim(0, max(ylim_top, y + 3 * h))
    else:
        ax_box.set_ylim(0, ylim_top)

    ax_box.set_title("Trial mean")
    ax_box.set_ylabel("Mean H-bond frequency")

    fig.suptitle(f"{residue}", fontsize=14)
    fig.tight_layout()

    fig.savefig(
        f"./figures/residue_hbond_compare/residue_{residue_index_rna:02d}_{residue}_hbond_compare.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)