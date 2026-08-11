import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# 读取之前保存的表格
df_mean_kJ = pd.read_csv("./figures/g_stds_mean_25combinations_kJ.csv", index_col=0)

# 提取数据矩阵
mean_matrix_kJ = df_mean_kJ.values

# 定义参数选项（从表格的列名和行名提取）
lagtime_options = [int(col.replace('lag=', '')) for col in df_mean_kJ.columns]
n_cluster_options = [int(row.replace('n=', '')) for row in df_mean_kJ.index]

# 绘制热图
fig2, ax2 = plt.subplots(figsize=(10, 8))
im = ax2.imshow(mean_matrix_kJ, cmap='coolwarm', aspect='auto',
                vmin=np.nanmin(mean_matrix_kJ), vmax=np.nanmax(mean_matrix_kJ))

# 设置坐标轴
ax2.set_xticks(range(len(lagtime_options)))
ax2.set_yticks(range(len(n_cluster_options)))
ax2.set_xticklabels([f"Lag={l}" for l in lagtime_options], fontsize=11)
ax2.set_yticklabels([f"n={n}" for n in n_cluster_options], fontsize=11)
ax2.set_xlabel("Lagtime", fontsize=13)
ax2.set_ylabel("Number of Clusters", fontsize=13)
ax2.set_title("ΔG Binding Free Energy (kJ/mol) for Different Parameter Combinations", fontsize=15)

# 在热图上显示数值
for i in range(len(n_cluster_options)):
    for j in range(len(lagtime_options)):
        if not np.isnan(mean_matrix_kJ[i, j]):
            value = mean_matrix_kJ[i, j]
            # 根据数值大小选择文字颜色（提高可读性）
            if abs(value - np.nanmean(mean_matrix_kJ)) < 5:
                text_color = 'black'
            else:
                text_color = 'white'
            ax2.text(j, i, f"{value:.2f}",
                    ha="center", va="center", 
                    color=text_color,
                    fontsize=18, fontweight='bold')

# 添加颜色条
plt.colorbar(im, label="ΔG (kJ/mol)", fraction=0.046, pad=0.04)

# 保存图片
fig2.tight_layout()
fig2.savefig("./figures/heatmap_mean_only_kJ.png", dpi=400, bbox_inches="tight")
plt.show()

print("热图已保存为: ./figures/heatmap_mean_only_kJ.png")