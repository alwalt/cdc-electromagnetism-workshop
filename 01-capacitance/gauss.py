import numpy as np
import matplotlib.pyplot as plt

# Constants
k = 8.99e9          # Coulomb's constant (N·m²/C²)
Q = 1e-6            # Total charge (C)
R = 1.0             # Sphere radius (m)

# Observation point (outside the sphere)
point = np.array([2.0, 0.0, 0.0])

# ----------------------------
# Coulomb's Law (Numerical)
# ----------------------------

N = 5000                    # Number of tiny charges
dq = Q / N                  # Charge per particle

# Randomly distribute charges uniformly inside the sphere
charges = []

while len(charges) < N:
    p = np.random.uniform(-R, R, 3)
    if np.linalg.norm(p) <= R:
        charges.append(p)

charges = np.array(charges)

E = np.zeros(3)

for r_charge in charges:
    r = point - r_charge
    distance = np.linalg.norm(r)
    E += k * dq * r / distance**3

E_coulomb = np.linalg.norm(E)

# ----------------------------
# Gauss's Law
# ----------------------------

r = np.linalg.norm(point)

E_gauss = k * Q / r**2

print(f"Coulomb (numerical): {E_coulomb:.2f} N/C")
print(f"Gauss (exact):       {E_gauss:.2f} N/C")
print(f"Percent Error: {100*abs(E_coulomb-E_gauss)/E_gauss:.2f}%")

r = np.linspace(1.1, 5, 100)

E = k * Q / r**2

plt.plot(r, E)
plt.xlabel("Distance from center (m)")
plt.ylabel("Electric Field (N/C)")
plt.title("Electric Field Outside a Uniformly Charged Sphere")
plt.grid(True)
plt.show()

# ---------------------------------------
# Plot 1: Coulomb's Law Visualization
# ---------------------------------------
fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, projection='3d')

# Draw the tiny charges
ax.scatter(charges[:,0], charges[:,1], charges[:,2],
           s=4, color='red', alpha=0.4, label='Tiny Charges')

# Draw observation point
ax.scatter(point[0], point[1], point[2],
           s=80, color='blue', label='Observation Point')

# Draw contribution vectors from a sample of charges
sample = charges[np.random.choice(N, 80, replace=False)]

for c in sample:
    direction = point - c
    direction = direction / np.linalg.norm(direction)

    ax.quiver(c[0], c[1], c[2],
              direction[0], direction[1], direction[2],
              length=0.3,
              color='purple',
              alpha=0.4)

ax.set_title("Coulomb's Law\nAdd contributions from every tiny charge")
ax.set_xlim(-1.5,2.5)
ax.set_ylim(-1.5,1.5)
ax.set_zlim(-1.5,1.5)
ax.legend()

plt.show()

# ---------------------------------------
# Plot 2: Gauss's Law Visualization
# ---------------------------------------
fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, projection='3d')

# Draw Gaussian sphere
u = np.linspace(0,2*np.pi,40)
v = np.linspace(0,np.pi,20)

x = 2*np.outer(np.cos(u),np.sin(v))
y = 2*np.outer(np.sin(u),np.sin(v))
z = 2*np.outer(np.ones_like(u),np.cos(v))

ax.plot_surface(x,y,z,
                color='lightgreen',
                alpha=0.25)

# Electric field arrows
phi = np.linspace(0,2*np.pi,12)
theta = np.linspace(0,np.pi,6)

for t in theta:
    for p in phi:

        px = 2*np.sin(t)*np.cos(p)
        py = 2*np.sin(t)*np.sin(p)
        pz = 2*np.cos(t)

        r = np.array([px,py,pz])
        r = r/np.linalg.norm(r)

        ax.quiver(px,py,pz,
                  r[0],r[1],r[2],
                  length=0.5,
                  color='green')

# Charge at center
ax.scatter(0,0,0,color='red',s=100)

ax.set_title("Gauss's Law\nField has the same magnitude everywhere on the sphere")
ax.set_xlim(-3,3)
ax.set_ylim(-3,3)
ax.set_zlim(-3,3)

plt.show()

# ---------------------------------------
# Plot 3: Build the electric field one
# charge at a time
# ---------------------------------------

running_E = []
E = np.zeros(3)

for c in charges:

    r = point - c
    distance = np.linalg.norm(r)

    E += k*dq*r/distance**3

    running_E.append(np.linalg.norm(E))

plt.figure(figsize=(8,4))
plt.plot(running_E)

plt.xlabel("Number of Tiny Charges Added")
plt.ylabel("Electric Field Magnitude (N/C)")
plt.title("Coulomb's Law: Building the Electric Field")
plt.grid(True)

plt.show()