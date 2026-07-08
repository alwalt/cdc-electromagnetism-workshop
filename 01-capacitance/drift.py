from vpython import *
import random
from math import pi, cos, sin

# ============================
# VPython Electron Drift Lab
# ============================

scene.title = "Electron Drift Speed vs Voltage and Temperature"
scene.width = 750
scene.height = 500
scene.background = color.white
scene.range = 10
scene.align = 'left'

# ----------------------------
# Graph (created before caption so it floats beside the scene)
# ----------------------------
g = graph(
    title="Electron Drift Speed (Drude Model)",
    xtitle="simulation time",
    ytitle="drift speed (μm/s)",
    width=480,
    height=500,
    align='right'
)

drift_curve = gcurve(color=color.blue)

# ----------------------------
# Simulation parameters
# ----------------------------
N_electrons = 60
Nx = 16
Ny = 5

wire_length = 18
wire_height = 6
dt = 0.04

voltage = 3.4
temperature = 20
paused = False
show_trails = False
smoothed_drift = 0.0   # exponential moving average of mean drift speed

# ----------------------------
# Physical wire parameters — copper, 60 m long, 1 mm² cross-section
# Gives realistic classroom values: ~250 μm/s and ~3 A at 3.4 V, 20 °C
# ----------------------------
WIRE_PHYS_LENGTH = 60.0    # m
WIRE_PHYS_AREA   = 1.0e-6  # m²  (1 mm diameter equivalent)
N_DENSITY        = 8.5e28  # free electrons/m³ (copper)
E_CHARGE         = 1.6e-19 # C
MOBILITY_0       = 4.4e-3  # m²/(V·s) at 20 °C (copper)
ALPHA_COPPER     = 3.9e-3  # /°C  temperature coefficient of resistivity
RESISTIVITY_0    = 1.7e-8  # Ω·m at 20 °C (copper)

# ----------------------------
# UI controls
# ----------------------------

scene.append_to_caption("\nVoltage\n")

def set_voltage(s):
    global voltage
    voltage = s.value
    voltage_text.text = f" {voltage:.1f} V"

voltage_slider = slider(min=0, max=10, value=voltage, length=300, bind=set_voltage)
voltage_text = wtext(text=f" {voltage:.1f} V")

scene.append_to_caption("\n\nTemperature\n")

def set_temperature(s):
    global temperature
    temperature = s.value
    temp_text.text = f" {temperature:.0f} °C"

temp_slider = slider(min=0, max=300, value=temperature, length=300, bind=set_temperature)
temp_text = wtext(text=f" {temperature:.0f} °C")

scene.append_to_caption("\n\n")

def toggle_pause(b):
    global paused
    paused = not paused
    b.text = "Resume" if paused else "Pause"

button(text="Pause", bind=toggle_pause)

scene.append_to_caption("   ")

def toggle_trails(c):
    global show_trails
    show_trails = c.checked
    for e in electrons:
        e.make_trail = show_trails
        if not show_trails:
            e.clear_trail()

checkbox(text="Show Trails", bind=toggle_trails)

scene.append_to_caption("\n\n")

# ----------------------------
# Wire boundary
# ----------------------------
box(
    pos=vector(0, 0, 0),
    size=vector(wire_length, wire_height, 0.05),
    color=color.gray(0.9),
    opacity=0.25
)

# ----------------------------
# Metal lattice ions
# ----------------------------
ions = []

for i in range(Nx):
    for j in range(Ny):
        pos = vector(
            -wire_length/2 + i * wire_length/(Nx-1),
            -wire_height/2 + j * wire_height/(Ny-1),
            0
        )

        ion = sphere(
            pos=pos,
            radius=0.15,
            color=color.gray(0.45)
        )

        ion.equilibrium = vector(pos.x, pos.y, pos.z)
        ions.append(ion)

# ----------------------------
# Electrons
# ----------------------------
electrons = []

def random_velocity():
    thermal_speed = 0.7 + 0.003 * temperature
    angle = random.uniform(0, 2*pi)
    return thermal_speed * vector(cos(angle), sin(angle), 0)

for i in range(N_electrons):
    e = sphere(
        radius=0.09,
        color=color.blue,
        make_trail=show_trails,
        retain=30,
        pos=vector(
            random.uniform(-wire_length/2, wire_length/2),
            random.uniform(-wire_height/2, wire_height/2),
            0
        )
    )

    e.v = random_velocity()
    electrons.append(e)

# ----------------------------
# Electric field arrow
# ----------------------------
field_arrow = arrow(
    pos=vector(-8, -4.7, 0),
    axis=vector(4, 0, 0),
    color=color.red,
    shaftwidth=0.08
)

field_label = label(
    pos=vector(-6, -3.9, 0),
    text="Electric field →",
    box=False,
    color=color.red,
    height=13
)

# ----------------------------
# Data display
# ----------------------------
info = label(
    pos=vector(0, 4.7, 0),
    text="",
    box=False,
    height=16,
    color=color.black
)

# ----------------------------
# Reset button
# ----------------------------

def reset_simulation(b):
    global electrons, t, smoothed_drift

    for e in electrons:
        e.visible = False

    electrons = []

    for i in range(N_electrons):
        e = sphere(
            radius=0.09,
            color=color.blue,
            make_trail=show_trails,
            retain=30,
            pos=vector(
                random.uniform(-wire_length/2, wire_length/2),
                random.uniform(-wire_height/2, wire_height/2),
                0
            )
        )
        e.v = random_velocity()
        electrons.append(e)

    drift_curve.delete()
    t = 0
    smoothed_drift = 0.0

button(text="Reset", bind=reset_simulation)

# ----------------------------
# Main loop
# ----------------------------
t = 0

while True:
    rate(100)

    if paused:
        continue

    # Temperature effects
    thermal_speed = 0.7 + 0.003 * temperature
    ion_vibration = 0.003 * temperature
    collision_radius = 0.22 + 0.0005 * temperature

    # Voltage effect
    drift_acceleration = 0.015 * voltage

    # Vibrate ions
    for ion in ions:
        ion.pos = ion.equilibrium + vector(
            random.uniform(-ion_vibration, ion_vibration),
            random.uniform(-ion_vibration, ion_vibration),
            0
        )

    vx_total = 0
    collision_count = 0

    for e in electrons:

        # Electric field gives a small average push
        e.v.x += drift_acceleration * dt

        # Move electron
        e.pos += e.v * dt

        # Bounce off top/bottom of wire
        if e.pos.y > wire_height/2:
            e.pos.y = wire_height/2
            e.v.y *= -1

        if e.pos.y < -wire_height/2:
            e.pos.y = -wire_height/2
            e.v.y *= -1

        # Wrap around left/right ends of wire
        if e.pos.x > wire_length/2:
            e.pos.x = -wire_length/2

        if e.pos.x < -wire_length/2:
            e.pos.x = wire_length/2

        # Collisions with vibrating ions
        for ion in ions:
            if mag(e.pos - ion.pos) < collision_radius:
                angle = random.uniform(0, 2*pi)

                # Scatter electron randomly
                e.v = thermal_speed * vector(cos(angle), sin(angle), 0)

                collision_count += 1
                break

        vx_total += e.v.x

    mean_drift_speed = vx_total / N_electrons

    # Smooth the drift speed so changes are clearly visible when sliders move
    smoothed_drift = 0.08 * mean_drift_speed + 0.92 * smoothed_drift

    # --- Drude model: physically accurate values for copper wire ---
    mobility   = MOBILITY_0 / (1 + ALPHA_COPPER * (temperature - 20))
    E_field    = voltage / WIRE_PHYS_LENGTH                              # V/m
    v_d_um_s   = mobility * E_field * 1e6                               # μm/s
    resistivity = RESISTIVITY_0 * (1 + ALPHA_COPPER * (temperature - 20))
    resistance  = resistivity * WIRE_PHYS_LENGTH / WIRE_PHYS_AREA       # Ω
    current     = voltage / resistance if resistance > 0 else 0         # A

    info.text = (
        f"Voltage = {voltage:.1f} V    "
        f"Electric field = {E_field:.4f} V/m\n"
        f"Drift speed = {v_d_um_s:.1f} μm/s    "
        f"Current = {current:.2f} A    "
        f"Resistance = {resistance:.2f} Ω\n"
        f"Temperature = {temperature:.0f} °C    "
        f"Collisions this frame = {collision_count}"
    )

    drift_curve.plot(t, v_d_um_s)

    t += dt