import pickle
import os
import mdtraj as md
import numpy as np
import matplotlib.pyplot as plt


N_TIMESTEP_IN_REPLICA = 201
TEMPERATURE = 300

pickle_dir = "./pickle-cache/binding-free-energy_1d"
if not os.path.exists(pickle_dir):
    os.mkdir(pickle_dir)

pacs_com_distances = []
pacs_com_vectors = []
for trial in range(20):
    pickle_com_distances = pickle.load(open(f"./pickle-cache/com-features/pacs_com_distances_{trial}.pickle", "rb"))
    pacs_com_distances.append(pickle_com_distances.reshape((-1, N_TIMESTEP_IN_REPLICA, 1)))
    pickle_com_vectors = pickle.load(open(f"./pickle-cache/com-features/pacs_com_vectors_{trial}.pickle", "rb"))
    pacs_com_vectors.append(pickle_com_vectors.reshape((-1, N_TIMESTEP_IN_REPLICA, 3)))

trajs = pacs_com_distances

from sklearn.cluster import KMeans
import matplotlib


def cluster_trajs(trajs, n_clusters):
    clustering_model = KMeans(
        n_clusters=n_clusters,
        init="k-means++",
        n_init=10,
        max_iter=int(1e10),
        tol=1e-10,
        verbose=0,
        random_state=1,
        copy_x=True,
        algorithm="lloyd"
    )
    trajs_concat = np.concatenate(trajs)
    clustered_trajs_concat = clustering_model.fit_predict(trajs_concat)
    return clustered_trajs_concat.reshape(len(trajs), N_TIMESTEP_IN_REPLICA), clustering_model.cluster_centers_


def plot_clusters(ax, trajs, clustered_trajs, cluster_centers):
    trajs_concat = np.concatenate(trajs)
    clustered_trajs_concat = np.concatenate(clustered_trajs)
    ax.hist(trajs_concat, bins=n_clusters*5)
    for cluster_center in cluster_centers:
        ax.axvline(x=cluster_center, color="black", linewidth=0.2)

from deeptime.markov import TransitionCountEstimator
from deeptime.markov.msm import MaximumLikelihoodMSM
from deeptime.markov.tools import estimation
from deeptime.util.validation import implied_timescales
import deeptime.plots


def construct_msm(clustered_trajs, lagtimes):
    msm_models = {}
    stationary_distributions = {}
    for lagtime in lagtimes:
        count_estimator = TransitionCountEstimator(
            lagtime=lagtime,
            count_mode="sliding",
            n_states=None,
            sparse=False,
        )
        count_estimator.fit(clustered_trajs)
        count_model = count_estimator.fetch_model()
        msm_constructor = MaximumLikelihoodMSM(
            reversible=True,
            stationary_distribution_constraint=None,
            sparse=False,
            allow_disconnected=False,
            maxiter=int(1e10),
            maxerr=1e-10,
            connectivity_threshold=0,
            transition_matrix_tolerance=1e-10,
            lagtime=None,
            use_lcc=False,
        ) 
        try:
            msm_constructor.fit(count_model)
        except:
            continue
        msm_models[lagtime] = msm_constructor.fetch_model()
        largest_connected_set = estimation.largest_connected_set(count_model.count_matrix, directed=True)
        stationary_distributions[lagtime] = np.zeros(np.max(clustered_trajs)+1)
        stationary_distributions[lagtime][largest_connected_set] = msm_models[lagtime].stationary_distribution
    return msm_models, stationary_distributions


def plot_implied_timescales(ax, msm_models):
    deeptime.plots.plot_implied_timescales(
        implied_timescales(list(msm_models.values())),
        n_its=10,
        ax=ax,
        process=None,
        show_mle=True,
        show_sample_mean=True,
        show_sample_confidence=True,
        show_cutoff=True,
        sample_confidence=0.95,
        colors=None,
    )
    ax.set_xlim(0, np.max(list(msm_models.keys())))
    ax.set_yscale("log")


n_clusters_candidates = [100, 80, 60, 40, 20]

if False:
    clustered_trajs = [None for _ in range(len(trajs))]
    cluster_centers = [None for _ in range(len(trajs))]
    for trial in range(len(trajs)):
        clustered_trajs[trial] = {}
        cluster_centers[trial] = {}
        for i_clusters, n_clusters in enumerate(n_clusters_candidates):
            print(trial, n_clusters)
            clustered_trajs[trial][n_clusters], cluster_centers[trial][n_clusters] = cluster_trajs(trajs[trial], n_clusters)
    pickle.dump(clustered_trajs, open(f"{pickle_dir}/clustered_trajs.pickle", "wb"))
    pickle.dump(cluster_centers, open(f"{pickle_dir}/cluster_centers.pickle", "wb"))

clustered_trajs = pickle.load(open(f"{pickle_dir}/clustered_trajs.pickle", "rb"))
cluster_centers = pickle.load(open(f"{pickle_dir}/cluster_centers.pickle", "rb"))


fig_cluster, ax_cluster = plt.subplots(len(trajs), len(n_clusters_candidates))
fig_cluster.set_size_inches(4*len(n_clusters_candidates), 4*len(trajs))

for trial in range(len(trajs)):
    for i_clusters, n_clusters in enumerate(n_clusters_candidates):
        plot_clusters(ax_cluster[trial][i_clusters], trajs[trial], clustered_trajs[trial][n_clusters], cluster_centers[trial][n_clusters])
        ax_cluster[trial][i_clusters].set_title(f"{trial}-{n_clusters}")

fig_cluster.tight_layout()
fig_cluster.savefig("figures/clusters2_all.png", dpi=300)
plt.close(fig_cluster)


if False:
    msm_models = [None for _ in range(len(trajs))]
    stationary_distributions = [None for _ in range(len(trajs))]
    for trial in range(len(trajs)):
        msm_models[trial] = {}
        stationary_distributions[trial] = {}
        for i_clusters, n_clusters in enumerate(n_clusters_candidates):
            print(trial, n_clusters)
            msm_models[trial][n_clusters], stationary_distributions[trial][n_clusters] = construct_msm(clustered_trajs[trial][n_clusters], range(2, int(N_TIMESTEP_IN_REPLICA/2), 2))
    pickle.dump(msm_models, open(f"{pickle_dir}/msm_models.pickle", "wb"))
    pickle.dump(stationary_distributions, open(f"{pickle_dir}/stationary_distributions.pickle", "wb"))

msm_models = pickle.load(open(f"{pickle_dir}/msm_models.pickle", "rb"))
stationary_distributions = pickle.load(open(f"{pickle_dir}/stationary_distributions.pickle", "rb"))


fig_its, ax_its = plt.subplots(len(trajs), len(n_clusters_candidates))
fig_its.set_size_inches(4*len(n_clusters_candidates), 4*len(trajs))

for trial in range(len(trajs)):
    for i_clusters, n_clusters in enumerate(n_clusters_candidates):
        plot_implied_timescales(ax_its[trial][i_clusters], msm_models[trial][n_clusters])
        ax_its[trial][i_clusters].set_title(f"{trial}-{n_clusters}")

fig_its.tight_layout()
fig_its.savefig("figures/its_all.png", dpi=300)
plt.close(fig_its)

import scipy.constants
from scipy.spatial import ConvexHull


def calculate_pmf(stationary_distributions):
    pmf = -np.log(stationary_distributions/max(stationary_distributions))
    pmf *= scipy.constants.Boltzmann
    pmf *= TEMPERATURE
    pmf *= scipy.constants.Avogadro
    pmf /= scipy.constants.calorie
    pmf /= 1000
    return pmf


def calculate_pmf_plot(cluster_centers, pmf, unbound_threshold):
    com_distances_cluster_centers = np.linalg.norm(cluster_centers, axis=1)
    indices_order = np.argsort(com_distances_cluster_centers)
    ordered_pmf = pmf[indices_order]
    ordered_cluster_centers = com_distances_cluster_centers[indices_order]
    pmf_baseline = []
    for i_cluster_center, (cluster_center, _pmf) in enumerate(zip(ordered_cluster_centers, ordered_pmf)):
        if unbound_threshold < cluster_center and np.isfinite(_pmf):
            pmf_baseline.append(_pmf)
    ordered_pmf -= np.mean(pmf_baseline)
    return ordered_cluster_centers, ordered_pmf


def plot_pmf(ax, ordered_cluster_centers, ordered_pmf, xmin, xmax, ymin, ymax, bound_threshold=None, unbound_threshold=None):
    ax.hlines(0, xmin=xmin, xmax=xmax, color="black")
    if bound_threshold != None and unbound_threshold != None:
        ax.vlines(bound_threshold,   ymin=ymin, ymax=ymax, color="black", linestyles="--")
        ax.vlines(unbound_threshold, ymin=ymin, ymax=ymax, color="black", linestyles="--")
    ax.plot(ordered_cluster_centers, ordered_pmf)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)


def calculate_g_pmf(cluster_centers, stationary_distributions, bound_threshold, unbound_threshold):
    bound_probability = 0
    unbound_probability = 0
    for cluster_center, stationary_distribution in zip(cluster_centers, stationary_distributions):
        com_distances_cluster_centers = np.linalg.norm(cluster_center) 
        if com_distances_cluster_centers < bound_threshold:
            bound_probability += stationary_distribution
        if  unbound_threshold < com_distances_cluster_centers:
            unbound_probability += stationary_distribution
    g_pmf = -np.log(bound_probability/unbound_probability)
    g_pmf *= scipy.constants.Boltzmann
    g_pmf *= TEMPERATURE
    g_pmf *= scipy.constants.Avogadro
    g_pmf /= scipy.constants.calorie
    g_pmf /= 1000
    return g_pmf


def calculate_volume_correction(com_vectors, unbound_threshold):
    unbound_com_vectors = com_vectors[unbound_threshold < np.linalg.norm(com_vectors, axis=2)]
    hull = ConvexHull(unbound_com_vectors)
    volume_correction = -np.log(hull.volume/1.661)
    volume_correction *= scipy.constants.Boltzmann
    volume_correction *= TEMPERATURE
    volume_correction *= scipy.constants.Avogadro
    volume_correction /= scipy.constants.calorie
    volume_correction /= 1000
    return volume_correction


pmfs = [None for _ in range(len(trajs))]

for trial in range(len(trajs)):
    print(trial)
    pmfs[trial] = {}
    for i_clusters, n_clusters in enumerate(n_clusters_candidates):
        pmfs[trial][n_clusters] = {}
        for lagtime in stationary_distributions[trial][n_clusters]:
            try:
                pmfs[trial][n_clusters][lagtime] = calculate_pmf(stationary_distributions[trial][n_clusters][lagtime])
            except:
                print("failed")
                continue

bound_thresholds = [1.5 for _ in range(len(trajs))]
unbound_thresholds = [3.0 for _ in range(len(trajs))]

import numpy as np
import matplotlib.pyplot as plt
from itertools import product
import pandas as pd
import seaborn as sns

# 定义要尝试的参数组合
n_cluster_options = [20, 40, 60, 80, 100]
lagtime_options = [20, 40, 60, 80, 100]

# 存储每个参数组合在所有trials上的结果
# 维度: [n_cluster_index][lagtime_index] -> 所有trials的g_std值列表
results_dict = {}

# 初始化结果字典
for i, n_cluster in enumerate(n_cluster_options):
    for j, lagtime in enumerate(lagtime_options):
        results_dict[(n_cluster, lagtime)] = []

# 遍历所有trials
for trial in range(len(trajs)):
    print(f"\n{'='*60}")
    print(f"Processing Trial {trial+1}/{len(trajs)}")
    print('='*60)
    
    # 为当前trial创建5x5的PMF图
    fig_grid, axes_grid = plt.subplots(len(n_cluster_options), len(lagtime_options), figsize=(20, 20))
    
    # 遍历所有参数组合
    for i, n_cluster in enumerate(n_cluster_options):
        for j, lagtime in enumerate(lagtime_options):
            print(f"  尝试 n_cluster={n_cluster}, lagtime={lagtime}")
            
            try:
                # 尝试计算PMF
                ordered_cluster_centers, ordered_pmf = calculate_pmf_plot(
                    cluster_centers[trial][n_cluster], 
                    pmfs[trial][n_cluster][lagtime], 
                    unbound_thresholds[trial]
                )
                
                # 计算g_pmf和volume_correction
                g_pmf = calculate_g_pmf(
                    cluster_centers[trial][n_cluster], 
                    stationary_distributions[trial][n_cluster][lagtime], 
                    bound_thresholds[trial], 
                    unbound_thresholds[trial]
                )
                volume_correction = calculate_volume_correction(
                    pacs_com_vectors[trial], 
                    unbound_thresholds[trial]
                )
                g_std = g_pmf + volume_correction
                
                # 存储结果 (单位: kcal/mol)
                results_dict[(n_cluster, lagtime)].append(g_std)
                
                # 绘制PMF
                plot_pmf(
                    axes_grid[i, j], 
                    ordered_cluster_centers, 
                    ordered_pmf, 
                    0, 5, -14, 3,
                    bound_threshold=bound_thresholds[trial], 
                    unbound_threshold=unbound_thresholds[trial]
                )
                axes_grid[i, j].set_title(f"n={n_cluster}, lag={lagtime}\nΔG={g_std:.2f} kcal/mol")
                
                print(f"    ✓ 成功！ΔG = {g_std:.2f} kcal/mol")
                
            except Exception as e:
                # 如果出错，记录NaN
                results_dict[(n_cluster, lagtime)].append(np.nan)
                axes_grid[i, j].text(0.5, 0.5, f"Failed\n{n_cluster}, {lagtime}", 
                                    ha='center', va='center', transform=axes_grid[i, j].transAxes)
                axes_grid[i, j].set_title(f"n={n_cluster}, lag={lagtime}\nFAILED")
                print(f"    ✗ 失败: {str(e)[:50]}...")
    
    # 保存当前trial的PMF图
    fig_grid.tight_layout(pad=2.0, w_pad=1.5, h_pad=2.0)
    fig_grid.savefig(f"./figures/pmf_grid_trial_{trial+1}_all_combinations.png", dpi=400, bbox_inches="tight")
    plt.close(fig_grid)

# ============================================================
# 计算每个参数组合的mean和std (kcal/mol)
# ============================================================

conversion_factor = 4.184  # kcal -> kJ

# 创建矩阵用于热图
mean_matrix_kcal = np.zeros((len(n_cluster_options), len(lagtime_options)))
std_matrix_kcal = np.zeros((len(n_cluster_options), len(lagtime_options)))
mean_matrix_kJ = np.zeros((len(n_cluster_options), len(lagtime_options)))
std_matrix_kJ = np.zeros((len(n_cluster_options), len(lagtime_options)))

# 用于存储有效组合的数量
count_matrix = np.zeros((len(n_cluster_options), len(lagtime_options)))

for i, n_cluster in enumerate(n_cluster_options):
    for j, lagtime in enumerate(lagtime_options):
        values = results_dict[(n_cluster, lagtime)]
        valid_values = [v for v in values if not np.isnan(v)]
        
        if len(valid_values) > 0:
            mean_kcal = np.mean(valid_values)
            std_kcal = np.std(valid_values)
            
            mean_matrix_kcal[i, j] = mean_kcal
            std_matrix_kcal[i, j] = std_kcal
            mean_matrix_kJ[i, j] = mean_kcal * conversion_factor
            std_matrix_kJ[i, j] = std_kcal * conversion_factor
            count_matrix[i, j] = len(valid_values)
        else:
            mean_matrix_kcal[i, j] = np.nan
            std_matrix_kcal[i, j] = np.nan
            mean_matrix_kJ[i, j] = np.nan
            std_matrix_kJ[i, j] = np.nan
            count_matrix[i, j] = 0

# 打印所有结果
print("\n" + "="*60)
print("25个参数组合的统计结果 (kJ/mol)")
print("="*60)

# 创建DataFrame
df_mean_kJ = pd.DataFrame(
    mean_matrix_kJ,
    index=[f"n={n}" for n in n_cluster_options],
    columns=[f"lag={l}" for l in lagtime_options]
)

df_std_kJ = pd.DataFrame(
    std_matrix_kJ,
    index=[f"n={n}" for n in n_cluster_options],
    columns=[f"lag={l}" for l in lagtime_options]
)

df_count = pd.DataFrame(
    count_matrix,
    index=[f"n={n}" for n in n_cluster_options],
    columns=[f"lag={l}" for l in lagtime_options]
)

print("\n平均值 (kJ/mol):")
print(df_mean_kJ.round(2))

print("\n标准差 (kJ/mol):")
print(df_std_kJ.round(2))

print("\n成功计算的trial数:")
print(df_count)

# 保存表格
df_mean_kJ.to_csv("./figures/g_stds_mean_25combinations_kJ.csv")
df_std_kJ.to_csv("./figures/g_stds_std_25combinations_kJ.csv")
df_count.to_csv("./figures/g_stds_count_25combinations.csv")

# ============================================================
# 绘制热图
# ============================================================

# 1. 平均值热图 (kJ/mol)
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 平均值热图
im1 = axes[0].imshow(mean_matrix_kJ, cmap='coolwarm', aspect='auto', 
                     vmin=np.nanmin(mean_matrix_kJ), vmax=np.nanmax(mean_matrix_kJ))
axes[0].set_xticks(range(len(lagtime_options)))
axes[0].set_yticks(range(len(n_cluster_options)))
axes[0].set_xticklabels([f"{l}" for l in lagtime_options])
axes[0].set_yticklabels([f"{n}" for n in n_cluster_options])
axes[0].set_xlabel("Lagtime", fontsize=12)
axes[0].set_ylabel("Number of Clusters", fontsize=12)
axes[0].set_title("Mean ΔG (kJ/mol)", fontsize=14)

# 在热图上显示数值
for i in range(len(n_cluster_options)):
    for j in range(len(lagtime_options)):
        if not np.isnan(mean_matrix_kJ[i, j]):
            text = axes[0].text(j, i, f"{mean_matrix_kJ[i, j]:.1f}",
                               ha="center", va="center", color="black" if abs(mean_matrix_kJ[i, j]) < 20 else "white",
                               fontsize=10, fontweight='bold')

plt.colorbar(im1, ax=axes[0], label="ΔG (kJ/mol)")

# 标准差热图
im2 = axes[1].imshow(std_matrix_kJ, cmap='YlOrRd', aspect='auto',
                     vmin=0, vmax=np.nanmax(std_matrix_kJ))
axes[1].set_xticks(range(len(lagtime_options)))
axes[1].set_yticks(range(len(n_cluster_options)))
axes[1].set_xticklabels([f"{l}" for l in lagtime_options])
axes[1].set_yticklabels([f"{n}" for n in n_cluster_options])
axes[1].set_xlabel("Lagtime", fontsize=12)
axes[1].set_ylabel("Number of Clusters", fontsize=12)
axes[1].set_title("Std ΔG (kJ/mol)", fontsize=14)

# 在热图上显示数值
for i in range(len(n_cluster_options)):
    for j in range(len(lagtime_options)):
        if not np.isnan(std_matrix_kJ[i, j]):
            text = axes[1].text(j, i, f"{std_matrix_kJ[i, j]:.1f}",
                               ha="center", va="center", color="black" if std_matrix_kJ[i, j] < 5 else "white",
                               fontsize=10, fontweight='bold')

plt.colorbar(im2, ax=axes[1], label="Std (kJ/mol)")

fig.tight_layout()
fig.savefig("./figures/heatmap_25combinations_kJ.png", dpi=400, bbox_inches="tight")
plt.show()

# ============================================================
# 额外：只显示平均值的单独热图
# ============================================================

fig2, ax2 = plt.subplots(figsize=(10, 8))
im = ax2.imshow(mean_matrix_kJ, cmap='coolwarm', aspect='auto',
                vmin=np.nanmin(mean_matrix_kJ), vmax=np.nanmax(mean_matrix_kJ))

ax2.set_xticks(range(len(lagtime_options)))
ax2.set_yticks(range(len(n_cluster_options)))
ax2.set_xticklabels([f"Lag={l}" for l in lagtime_options], fontsize=11)
ax2.set_yticklabels([f"n={n}" for n in n_cluster_options], fontsize=11)
ax2.set_xlabel("Lagtime", fontsize=13)
ax2.set_ylabel("Number of Clusters", fontsize=13)
ax2.set_title("ΔG Binding Free Energy (kJ/mol) for Different Parameter Combinations", fontsize=15)

# 显示数值
for i in range(len(n_cluster_options)):
    for j in range(len(lagtime_options)):
        if not np.isnan(mean_matrix_kJ[i, j]):
            ax2.text(j, i, f"{mean_matrix_kJ[i, j]:.2f}",
                    ha="center", va="center", 
                    color="black" if abs(mean_matrix_kJ[i, j] - np.nanmean(mean_matrix_kJ)) < 5 else "white",
                    fontsize=11, fontweight='bold')

plt.colorbar(im, label="ΔG (kJ/mol)", fraction=0.046, pad=0.04)
fig2.tight_layout()
fig2.savefig("./figures/heatmap_mean_only_kJ.png", dpi=400, bbox_inches="tight")
plt.show()

# ============================================================
# 打印整体统计信息
# ============================================================

print("\n" + "="*60)
print("整体统计信息 (所有25个组合)")
print("="*60)

valid_means = mean_matrix_kJ[~np.isnan(mean_matrix_kJ)]
valid_stds = std_matrix_kJ[~np.isnan(std_matrix_kJ)]

print(f"所有组合的平均值 (kJ/mol):")
print(f"  Mean of means: {np.mean(valid_means):.4f} ± {np.std(valid_means):.4f}")
print(f"  Range: [{np.min(valid_means):.4f}, {np.max(valid_means):.4f}]")

print(f"\n所有组合的标准差 (kJ/mol):")
print(f"  Mean of stds: {np.mean(valid_stds):.4f} ± {np.std(valid_stds):.4f}")
print(f"  Range: [{np.min(valid_stds):.4f}, {np.max(valid_stds):.4f}]")

# 找出最佳和最差的参数组合
best_idx = np.unravel_index(np.nanargmin(mean_matrix_kJ), mean_matrix_kJ.shape)
worst_idx = np.unravel_index(np.nanargmax(mean_matrix_kJ), mean_matrix_kJ.shape)

print(f"\n最佳参数组合 (最负的ΔG):")
print(f"  n={n_cluster_options[best_idx[0]]}, lag={lagtime_options[best_idx[1]]}")
print(f"  ΔG = {mean_matrix_kJ[best_idx]:.4f} kJ/mol")

print(f"\n最差参数组合 (最正的ΔG):")
print(f"  n={n_cluster_options[worst_idx[0]]}, lag={lagtime_options[worst_idx[1]]}")
print(f"  ΔG = {mean_matrix_kJ[worst_idx]:.4f} kJ/mol")

# ============================================================
# 可选：绘制每个参数组合的箱线图
# ============================================================

fig3, ax3 = plt.subplots(figsize=(14, 8))

# 准备数据
data_for_box = []
labels_for_box = []
for i, n_cluster in enumerate(n_cluster_options):
    for j, lagtime in enumerate(lagtime_options):
        values = results_dict[(n_cluster, lagtime)]
        valid_values = [v * conversion_factor for v in values if not np.isnan(v)]
        if len(valid_values) > 0:
            data_for_box.append(valid_values)
            labels_for_box.append(f"n={n_cluster}\nlag={lagtime}")

if data_for_box:
    bp = ax3.boxplot(data_for_box, labels=labels_for_box, patch_artist=True)
    ax3.set_xlabel("Parameter Combinations (n_cluster, lagtime)", fontsize=12)
    ax3.set_ylabel("ΔG (kJ/mol)", fontsize=12)
    ax3.set_title("Distribution of ΔG for Each Parameter Combination", fontsize=14)
    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    fig3.tight_layout()
    fig3.savefig("./figures/boxplot_25combinations_kJ.png", dpi=400, bbox_inches="tight")
    plt.show()

print("\n所有图片和表格已保存到 ./figures/ 目录")
print("="*60)