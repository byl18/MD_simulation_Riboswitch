#!/bin/bash
#SBATCH -J job_name           # 作业名称
#SBATCH -p gpu                # 分区名称 (如 gpu, cpu)
#SBATCH -N 1                  # 节点数
#SBATCH --ntasks-per-node=1   # 每个节点的任务数
#SBATCH --cpus-per-task=4     # 每个任务的CPU核心数
#SBATCH --gres=gpu:1          # 每个节点申请的GPU卡数
#SBATCH -o %j.out             # 标准输出文件
#SBATCH -e %j.err             # 标准错误输出文件
#SBATCH --mem=8G              # 内存申请

