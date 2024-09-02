from matplotlib import pyplot as plt
import pandas as pd
import numpy as np


def rescale(min_val, max_val, x):
    return 100 * (x - min_val) / (max_val - min_val)


fasta_p_numbers = [58.07, 35.34, 40.87, 229.87, 99.136, 30.85, 237.15, 114.48,
                   49.30, 32.50, 42.92, 48.21, 59.10, 37.07, 246.38, 182.30, 249.66, 169.91]
fasta_c_js = [30.53, 53.61]
fasta_c_js_p = [ 35.34, 40.87, 32.50, 42.92, 48.21]
fasta_c_py = [30.53, 282.16]
fasta_c_py_p = [229.87, 99.136, 30.85, 37.07, 249.66, 169.91]
fasta_py_js = [53.61, 282.16]
fasta_py_js_p = [237.15, 114.48, 54.30, 59.10, 246.38, 182.30]

nbody_numbers = [14.91, 1612.46]
nbody_p_numbers = [15.69, 1592.358]

pidigits_numbers = [21.28, 93.91]
pidigits_p_numbers = [23.89, 94.51, 82.88, 79.27]


plt.figure()
plt.hlines(1, -10, 110)
# plt.axis("off")

for arr, arr_p in [(fasta_c_js, fasta_c_js_p), (fasta_c_py, fasta_c_py_p), (fasta_py_js, fasta_py_js_p), (nbody_numbers, nbody_p_numbers), (pidigits_numbers, pidigits_p_numbers)]:
    min_num = min(arr)
    max_num = max(arr)
    plt.eventplot([rescale(min_num, max_num, n) for n in arr_p],
                  orientation="horizontal", colors='b', linelengths=1)
    plt.eventplot([rescale(min_num, max_num, n) for n in arr],
                  orientation="horizontal", colors='r', linelengths=2)


plt.legend(["_nolegend_", "Polyglot scenarios",
           "Fastest & slowest non-polyglot scenarios"], loc="upper left")
# plt.eventplot(fasta_p_numbers, orientation="horizontal",
#               colors='b', linelengths=0.5)
# plt.eventplot(fasta_numbers, orientation="horizontal", colors='r')

plt.gca().get_yaxis().set_visible(False)

plt.xlabel("Scaled execution time %")

plt.savefig("benchmarks.png", bbox_inches="tight")
plt.show()
