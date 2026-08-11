#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import subprocess
import matplotlib as mpl
import argparse
mpl.rcParams['font.sans-serif'] = ['Nimbus Roman']
mpl.rcParams['font.weight'] = 'bold'  
mpl.rcParams['font.size'] = 15


plot_config = {
        "potential": {
            "ylabel": "Potential Energy (kJ/mol)",
            "title_suffix": "Potential Energy"
        },
        "pressure": {
            "ylabel": "Pressure (bar)",
            "title_suffix": "Pressure"
        },
        "temperature": {
            "ylabel": "Temperature (K)", 
            "title_suffix": "Temperature"
        },
        "distance": {
            "ylabel": "Distance (nm)",
            "title_suffix": "Distance"
        },
        "density": {
            "ylabel": "Density (kg/m³)",
            "title_suffix": "Density",
        }
    }

def main():
    parser = argparse.ArgumentParser(description='Plot MD simulation data. 用法: python plot_xvg.py -f your_file.xvg -t potential')
    parser.add_argument('--type', '-t', type=str, required=True,
                       choices=['potential', 'pressure', 'temperature', 'distance', 'density'],
                       help='Type of data to plot: potential, pressure, temperature, distance')
    parser.add_argument('--filename', '-f', type=str,
                       help='Input data filename')
    parser.add_argument('--output', '-o', type=str, default='./',
                       help='Output plot filename (optional)')
    parser.add_argument('--color', '-c', type=str, default='k',
                       help='Plot color (default: blue)')
    parser.add_argument('--combined', action='store_true',
                       help='Plot multiple npt files in one figure')
    parser.add_argument('--npt-range', type=str, default='1-10',
                       help='Range of npt directories to combine (e.g., 1-10)')
    args = parser.parse_args()
    if args.combined:
        plot_combined_npt(args)
    else:
        plot_md_data(args)




def read_filtered_xvg(filename):
    data_lines = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('@') and not line.startswith('#'):
                data_lines.append(line)
    return data_lines


def plot_md_data(args):
    filename = args.filename
    data_lines = read_filtered_xvg(filename)
    if data_lines:
        data = np.array([list(map(float, line.split())) for line in data_lines])
    else:
        print("Error: no valid data")
        sys.exit(1)
    plt.figure(figsize=(5, 3))
    config = plot_config.get(args.type, plot_config["potential"])
    if data.ndim > 1 and data.shape[1] > 1:
        for i in range(1, data.shape[1]):
            plt.plot(data[:, 0], data[:, i], label=config["title_suffix"], color=args.color)
    else:
        plt.plot(data,label = config["title_suffix"], color=args.color)
    plt.xlabel('Time (ps)', fontweight = 'bold')
    plt.ylabel(config["ylabel"], fontweight = 'bold') 
    # plt.title(f'{config["title_suffix"]} - {args.output}', fontweight = 'bold', pad =25)
    # plt.legend()
    plt.grid(True, alpha=0.3)
    output_name = args.output + '_' + args.type + '.png'
    plt.savefig(output_name, dpi=300, bbox_inches='tight')
    print(f"Figure saved as: {output_name}")



def plot_combined_npt(args):
    start, end = map(int, args.npt_range.split('-'))
    npt_files = []
    for i in range(start, end + 1):
        if args.type == 'density':
            file_path = f"/gs/bs/tga-Kitao-Lab/yilan/projects/SAM/EEM//5_npt-{i}/densDensityity.xvg"
        else:
            file_path = f"/gs/bs/tga-Kitao-Lab/yilan/projects/SAM/EEM//5_npt-{i}/{args.type.capitalize()}.xvg"
        if os.path.exists(file_path):
            npt_files.append(file_path)
        else:
            print(f"Warning: file not exists {file_path}")
    if not npt_files:
        print("Error: not found npt file")
        return
    plt.figure(figsize=(8, 4))
    config = plot_config.get(args.type, plot_config["potential"])
    time_offset = 0
    colors = plt.cm.tab10(np.linspace(0, 1, len(npt_files)))
    for i, file_path in enumerate(npt_files):
        data_lines = read_filtered_xvg(file_path)
        if not data_lines:
            continue
        data = np.array([list(map(float, line.split())) for line in data_lines])
        if data.ndim > 1 and data.shape[1] > 1:
            time = data[:, 0] + time_offset
            y_data = data[:, 1] if data.shape[1] > 1 else data[:, 0]
        else:
            time = np.arange(len(data)) + time_offset
            y_data = data
        npt_num = file_path.split('5_npt-')[1].split('/')[0]
        label = f'NPT-{npt_num}'
        plt.plot(time, y_data, label=label, color=colors[i], linewidth=1.5)
        time_offset = time[-1] + 50
        if i < len(npt_files) - 1: 
            plt.axvline(x=time_offset - 25, color='gray', linestyle='--', alpha=0.7, linewidth=1)
    plt.xlabel('Time (ps)', fontweight='bold')
    plt.ylabel(config["ylabel"], fontweight='bold')
    # plt.title(f'{config["title_suffix"]} - Combined NPT {args.npt_range}', fontweight='bold', pad=25)
    # plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left') 
    plt.grid(True, alpha=0.3)
    if args.type == "temperature":
        plt.ylim(280, 320)
    elif args.type == "pressure":
        plt.ylim(-600, 600)
    elif args.type == "density":
        plt.ylim(980, 1020)
    plt.tight_layout()
    output_name = f"{args.output}combined_npt_{args.type}_{args.npt_range}.png"
    plt.savefig(output_name, dpi=300, bbox_inches='tight')
    print(f"Figure saved as: {output_name}")

if __name__ == "__main__":
    main()
