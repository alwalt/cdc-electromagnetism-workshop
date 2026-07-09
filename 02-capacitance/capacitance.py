import numpy as np
import matplotlib.pyplot as plt

# Define the parameters of the capacitor
d = 2.0  # distance between plates
sigma = 1.0  # charge density
epsilon_0 = 8.854e-12  # electric constant

# Define the positions of the charges on each plate
n_charges = 50
y_charges_pos = np.linspace(-d, d, n_charges)
y_charges_neg = np.linspace(-d, d, n_charges)
x_charges_pos = np.zeros_like(y_charges_pos) - d/2
x_charges_neg = np.zeros_like(y_charges_pos) + d/2

xlim = ylim = -5, 5

# Define a mesh grid of points
x, y = np.meshgrid(np.linspace(*xlim, 200), np.linspace(*ylim, 200))

# Compute the electric field vector
E_x = np.zeros_like(x)
E_y = np.zeros_like(y)

# Compute the electric field due to positive charges
for i in range(n_charges):
    r = np.sqrt((x-x_charges_pos[i])**2 + (y-y_charges_pos[i])**2)
    E_x += sigma / (2 * epsilon_0) * (x - x_charges_pos[i]) / r**3
    E_y += sigma / (2 * epsilon_0) * (y - y_charges_pos[i]) / r**3

# Compute the electric field due to negative charges
for i in range(n_charges):
    r = np.sqrt((x-x_charges_neg[i])**2 + (y-y_charges_neg[i])**2)
    E_x -= sigma / (2 * epsilon_0) * (x - x_charges_neg[i]) / r**3
    E_y -= sigma / (2 * epsilon_0) * (y - y_charges_neg[i]) / r**3

# Plot the electric field
fig = plt.figure(figsize=(8, 8), facecolor='k')
ax = fig.add_subplot(facecolor='k')
plt.axis('off')

ax.streamplot(x, y, E_x, E_y, 
              color=np.log(E_x**2 + E_y**2), linewidth=1, cmap='cool',
              density=3, arrowstyle='->', zorder=20
             )
ax.scatter(x_charges_pos, y_charges_pos, s=20, color='red')
ax.scatter(x_charges_neg, y_charges_neg, s=20, color='blue')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_xlim(*xlim)
ax.set_ylim(*ylim)
ax.set_aspect('equal')
plt.show()