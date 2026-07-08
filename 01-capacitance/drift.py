from vpython import *
import random

scene.width = 1000
scene.height = 500
scene.background = color.white

# ----------------------------
# PARAMETERS
# ----------------------------

N_electrons = 50
Nx = 15
Ny = 5

temperature = 0.5       # Increase this!
electric_field = 0.01   # Increase this!

wire_length = 18
wire_height = 6

dt = 0.05

# ----------------------------
# Metal lattice
# ----------------------------

ions = []

for i in range(Nx):
    for j in range(Ny):
        pos = vector(
            -wire_length/2 + i*wire_length/(Nx-1),
            -wire_height/2 + j*wire_height/(Ny-1),
            0
        )

        ion = sphere(
            pos=pos,
            radius=0.15,
            color=color.gray(0.5)
        )

        ion.equilibrium = pos
        ions.append(ion)

# ----------------------------
# Electrons
# ----------------------------

electrons = []

for i in range(N_electrons):

    e = sphere(
        radius=0.08,
        color=color.blue,
        make_trail=False,
        pos=vector(
            random.uniform(-wire_length/2, wire_length/2),
            random.uniform(-wire_height/2, wire_height/2),
            0
        )
    )

    e.v = vector(
        random.uniform(-1,1),
        random.uniform(-1,1),
        0
    )

    electrons.append(e)

drift_label = label(pos=vector(0,4,0), text="", box=False)

# ----------------------------
# MAIN LOOP
# ----------------------------

while True:

    rate(100)

    # Ions vibrate
    for ion in ions:

        ion.pos = ion.equilibrium + vector(
            random.uniform(-temperature,temperature)*0.08,
            random.uniform(-temperature,temperature)*0.08,
            0
        )

    vx_total = 0

    for e in electrons:

        # Electric field
        e.v.x += electric_field*dt

        # Move
        e.pos += e.v*dt

        # Bounce off walls
        if abs(e.pos.y) > wire_height/2:
            e.v.y *= -1

        # Wrap around wire
        if e.pos.x > wire_length/2:
            e.pos.x = -wire_length/2

        if e.pos.x < -wire_length/2:
            e.pos.x = wire_length/2

        # Collisions
        for ion in ions:

            if mag(e.pos-ion.pos) < 0.25:

                speed = mag(e.v)

                angle = random.uniform(0,2*pi)

                e.v = speed*vector(cos(angle), sin(angle),0)

                break

        vx_total += e.v.x

    drift = vx_total/N_electrons

    drift_label.text = (
        f"Temperature = {temperature:.2f}\n"
        f"Electric Field = {electric_field:.2f}\n"
        f"Average Drift = {drift:.3f}"
    )