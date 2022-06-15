# Standard import
import matplotlib.pyplot as plt

# Import 3D Axes
from mpl_toolkits.mplot3d import axes3d

# Set up Figure and 3D Axes
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Get some data
X, Y, Z = axes3d.get_test_data(0.1)

# Plot using Axes notation
ax.plot_wireframe(X, Y, Z)
plt.show()
