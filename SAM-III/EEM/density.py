import os
import subprocess
import re
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def get_replica_and_cv_from_log(log_file):
    """
    从 cv_ranked.log 的第一行提取 replica 编号和 cv 值。
    返回 (replica_num, cv_value) 或 (None, None)
    """
    try:
        with open(log_file, 'r') as f:
            first_line = f.readline().strip()
            # 匹配格式: replica 9 frame 3 cv 0.2796...
            match = re.search(r'replica\s+(\d+).*cv\s+([0-9.e-]+)', first_line)
            if match:
                replica_num = int(match.group(1))
                cv_value = float(match.group(2))
                return replica_num, cv_value
            else:
                return None, None
    except Exception as e:
        print(f"Error reading {log_file}: {e}")
        return None, None

def get_density_from_edr(edr_path, temp_xvg="temp_density.xvg"):
    """从单个 edr 文件提取最后一个时间点的密度 (kg/m^3)"""
    cmd = f"echo 'Density' | gmx_mpi energy -f {edr_path} -o {temp_xvg} -quiet"
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {edr_path}: {e.stderr}")
        return np.nan

    densities = []
    with open(temp_xvg, 'r') as f:
        for line in f:
            if line.startswith(('#', '@')):
                continue
            parts = line.split()
            if len(parts) >= 2:
                densities.append(float(parts[1]))
    os.remove(temp_xvg)

    if not densities:
        return np.nan
    return densities[-1]   # 最后一个时间点的密度

# 主程序
base_dir = Path("/gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/EEM/test_trial/pacs")
all_densities = {}   # trial_num -> list of densities
max_cycles = 0

for trial_num in range(1, 21):
    trial_dir = base_dir / f"trial{trial_num:03d}"
    if not trial_dir.exists():
        print(f"Warning: {trial_dir} not found")
        continue

    # 找到所有 cycle 目录
    cycles = sorted(trial_dir.glob("cycle*"))
    densities = []   # 按 cycle 顺序存储密度

    for cycle_dir in cycles:
        log_file = cycle_dir / "summary" / "cv_ranked.log"
        if not log_file.exists():
            print(f"Warning: {log_file} not found")
            densities.append(np.nan)
            continue

        replica_num, cv = get_replica_and_cv_from_log(log_file)
        if replica_num is None:
            print(f"Warning: Cannot parse {log_file}")
            densities.append(np.nan)
            continue

        # 构建对应 replica 的 edr 文件路径
        replica_dir = cycle_dir / f"replica{replica_num:03d}"   # 假设 replica 编号是三位数
        edr_file = replica_dir / "prd.edr"
        if not edr_file.exists():
            print(f"Warning: {edr_file} not found")
            densities.append(np.nan)
            continue

        density = get_density_from_edr(str(edr_file))
        densities.append(density)

    if densities:
        all_densities[trial_num] = densities
        max_cycles = max(max_cycles, len(densities))
        print(f"Trial {trial_num:03d}: {len(densities)} cycles")

# 绘图（与 CV 绘图格式一致）
fig, ax = plt.subplots(figsize=(12, 8))
colors = plt.cm.tab20(np.linspace(0, 1, len(all_densities)))

for i, (trial_num, dens_list) in enumerate(sorted(all_densities.items())):
    cycles_x = range(1, len(dens_list) + 1)
    ax.plot(cycles_x, dens_list, marker='o', markersize=3,
            linewidth=1.5, label=f"Trial {trial_num:03d}",
            color=colors[i])

ax.set_xlabel("Cycle", fontsize=14)
ax.set_ylabel("Density (kg/m³)", fontsize=14)
ax.set_title("Density vs Cycle (using same replica as cv_ranked.log)", fontsize=16)
ax.set_xlim(0.5, max_cycles + 0.5)
ax.grid(True, alpha=0.3)
ax.legend(loc='best', ncol=2, fontsize=8)

plt.tight_layout()
plt.savefig("density_curves_all_trials.png", dpi=300)
plt.savefig("density_curves_all_trials.pdf")
plt.show()

print(f"\nTotal trials plotted: {len(all_densities)}")