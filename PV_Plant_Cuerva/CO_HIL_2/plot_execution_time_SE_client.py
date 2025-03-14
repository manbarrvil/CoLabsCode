# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 17:42:20 2025

@author: sim-intel
"""

import matplotlib.pyplot as plt
import json
import numpy as np

# Open and load the json file
with open("data.json", "r") as file:
    data = json.load(file)

data = np.array(data)*1000

plt.style.use('_mpl-gallery')

# plot:
fig, ax = plt.subplots()
ax.hist(data, bins=8, linewidth=0.5, edgecolor="white")
ax.set_xlabel("Execution time (ms)", labelpad=10)
ax.set_ylabel("Frequency", labelpad=10)
plt.show()
fig.savefig("latency_SE.pdf", format="pdf")
fig.savefig("latency_SE.png", format="png")
fig.savefig("latency_SE.svg", format="svg")