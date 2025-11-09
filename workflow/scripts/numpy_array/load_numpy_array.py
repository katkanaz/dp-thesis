import numpy as np

# Load numpy files
data_super = np.load("results/clusters/FUC/super/FUC_all_pairs_rmsd_super.npy")
data_align = np.load("results/clusters/FUC/super/FUC_all_pairs_rmsd_super.npy")

# Print the content of the numpy arrays
print(f"align: {data_align.shape}")
print(f"len align: {len(data_align)}")
print(f"just data align: {data_align}")
print(f"super: {data_super.shape}")
print(f"len super: {len(data_super)}")
print(f"just data super: {data_super}")
