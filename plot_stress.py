from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

x_axis = [1, 10, 50, 100, 500, 1000, 1500, 2000]

numbers = pd.read_csv("stress.csv", header=None)


numbers.to_numpy()

# print(numbers)

plt.plot(x_axis, numbers.swapaxes(0, 1), marker="x")
plt.grid()

plt.xlabel("Number of iterations")
plt.ylabel("Execution time (seconds)")

plt.legend(["Python calling JavaScript", "Python calling C", "JavaScript calling Python",
           "JavaScript calling C", "C calling JavaScript", "C calling Python", "_nolegend_", "_nolegend_", "Pure C/JavaScript/Python"])

plt.savefig("stress_test.png", bbox_inches="tight")
plt.show()
