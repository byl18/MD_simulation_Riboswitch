# <<< MODIFIED: compare PreQ0 and PreQ1 in the same residue-wise figures
import os
import pickle
from scipy.stats import mannwhitneyu
import numpy as np
import matplotlib.pyplot as plt
import mdtraj as md

# <<< MODIFIED: set paths for two systems
systems = {
    "SAM": {
        "color": "red",
        "top": "/gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM/test_trial/2_md-preparation/gleap.target.gro",
        "pickle_dir": "/gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM/test_trial/pacs/post_analysis/pickle-cache/interactions_hbond",
    },
    "SAH": {
        "color": "blue",
        "top": "/gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAH/test_trial/2_md-preparation/gleap.target.gro",
        "pickle_dir": "/gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAH/test_trial/pacs/post_analysis/pickle-cache/interactions_hbond",
    },
    "EEM": {
        "color": "yellow",
        "top": "/gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/EEM/test_trial/2_md-preparation/gleap.target.gro",
        "pickle_dir": "/gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/EEM/test_trial/pacs/post_analysis/pickle-cache/interactions_hbond",
    },
}

n_trials = 20
n_bins = 120
ymax_line = 5.5

os.makedirs("./figures/residue_hbond_compare", exist_ok=True)


# <<< MODIFIED: function to load PaCS-MD interaction results for one system
def load_pacs_interactions(system_info):
    gleap_target = md.load(system_info["top"])
    atom_indices_ligand = gleap_target.topology.select("resid 52")
    atom_indices_rna = gleap_target.topology.select("resid 0 to 51")
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
ref_top = loaded["SAM"]["top"]

# <<< MODIFIED: plot one figure for each RNA residue
for residue_index_rna in range(52):
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
                alpha=0.9,
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
    ax_line.plot([], [], color="red", label="SAM")
    ax_line.plot([], [], color="blue", label="SAH")
    ax_line.plot([], [], color="yellow", label="EEM")

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
    # <<< MODIFIED: pairwise Mann–Whitney U-test among SAM, SAH, and EEM
    def p_to_star(p_value):
        if p_value < 0.0001:
            return "****"
        elif p_value < 0.001:
            return "***"
        elif p_value < 0.01:
            return "**"
        elif p_value < 0.05:
            return "*"
        else:
            return None

    comparisons = [
        (0, 1),  # SAM vs SAH
        (1, 2),  # SAM vs EEM
        (0, 2),  # SAH vs EEM
    ]

    y_box_max = max(
        np.nanmax(box_data[0]),
        np.nanmax(box_data[1]),
        np.nanmax(box_data[2])
    )

    h = y_box_max * 0.08
    if h == 0:
        h = 0.02

    y_current = y_box_max + h
    y_max_for_plot = ylim_top

    for idx1, idx2 in comparisons:
        u_stat, p_value = mannwhitneyu(
            box_data[idx1],
            box_data[idx2],
            alternative="two-sided"
        )

        sig_label = p_to_star(p_value)

        print(
            f"{box_labels[idx1]} vs {box_labels[idx2]}: "
            f"U = {u_stat:.2f}, p = {p_value:.5g}, sig = {sig_label}"
        )

        # only draw significant comparisons
        if sig_label is None:
            continue
        if idx1 == 0 and idx2 == 2:
            y_current += 10 * h
        x1 = idx1 + 1
        x2 = idx2 + 1

        ax_box.plot(
            [x1, x1, x2, x2],
            [y_current, y_current + h, y_current + h, y_current],
            color="black",
            linewidth=1.2,
        )

        ax_box.text(
            (x1 + x2) / 2,
            y_current + h,
            sig_label,
            ha="center",
            va="bottom",
            fontsize=14,
            fontweight="bold",
        )

        y_max_for_plot = max(y_max_for_plot, y_current + 3 * h)
        y_current += 3 * h

    ax_box.set_ylim(0, y_max_for_plot)

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