"""Interactive VPython model for self-capacitive touchscreen fringing fields.

Run:
    python 02-capacitance/touchscreen_vpython_demo.py

If needed:
    pip install vpython
"""

from __future__ import annotations

from math import isfinite

from vpython import arrow, box, canvas, color, rate, slider, sphere, vector, wtext

# Scene setup
scene = canvas(
    title="Self-Capacitive Touchscreen: Fringing Field Demo",
    width=1100,
    height=700,
    background=vector(0.08, 0.09, 0.12),
)
scene.caption = ""

# World objects
ELECTRODE_WIDTH = 14.0
ELECTRODE_Y = 0.0
ELECTRODE_SEGMENTS = 13

field_arrows = []

# Initial parameter values
state = {
    "drive_voltage": 1.0,
    "finger_x": 0.0,
    "finger_height": 3.0,
    "finger_radius": 1.2,
}

# Draw the sensing electrode (single plate)
electrode = box(
    pos=vector(0, ELECTRODE_Y, 0),
    size=vector(ELECTRODE_WIDTH, 0.16, 2.8),
    color=vector(0.15, 0.95, 1.0),
    opacity=0.6,
)

# Draw the finger as a grounded conductive body
finger = sphere(
    pos=vector(state["finger_x"], state["finger_height"], 0),
    radius=state["finger_radius"],
    color=vector(1.0, 0.9, 0.2),
    opacity=0.35,
)

info = None
x_text = None
height_text = None
radius_text = None
voltage_text = None


def clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def induced_finger_charge(v_drive: float, h: float, r: float) -> float:
    """Simple qualitative coupling model for induced negative charge."""
    coupling = r / (h + r + 0.25)
    return -0.9 * v_drive * coupling


def electric_field_at(point: vector) -> vector:
    """Approximate field from electrode segments plus grounded finger coupling."""
    v_drive = state["drive_voltage"]
    h = state["finger_height"]
    r = state["finger_radius"]

    e_total = vector(0, 0, 0)

    # Electrode approximated as point-charge segments along x
    q_seg = v_drive / ELECTRODE_SEGMENTS
    for i in range(ELECTRODE_SEGMENTS):
        x = -ELECTRODE_WIDTH / 2 + i * ELECTRODE_WIDTH / (ELECTRODE_SEGMENTS - 1)
        src = vector(x, ELECTRODE_Y, 0)
        dr = point - src
        dist = dr.mag
        if dist < 0.25:
            continue
        e_total += q_seg * dr / (dist**3)

    # Finger acts like a grounded conductor with induced opposite charge
    q_finger = induced_finger_charge(v_drive, h, r)
    drf = point - finger.pos
    distf = drf.mag
    if distf > 0.25:
        e_total += q_finger * drf / (distf**3)

    return e_total


def estimated_signal_pf() -> float:
    """Toy estimate for sensed capacitance change (for student intuition only)."""
    v_drive = abs(state["drive_voltage"])
    h = state["finger_height"]
    r = state["finger_radius"]
    coupling = r / (h + r + 0.25)
    return 0.4 + 6.0 * coupling * v_drive


def update_labels() -> None:
    x_text.text = f" {state['finger_x']:.2f}"
    height_text.text = f" {state['finger_height']:.2f}"
    radius_text.text = f" {state['finger_radius']:.2f}"
    voltage_text.text = f" {state['drive_voltage']:.2f}"

    delta_c = estimated_signal_pf()
    info.text = (
        "\nObservation: closer/larger finger increases fringing coupling to ground."
        f"\nEstimated signal change (toy model): {delta_c:.2f} pF"
    )


def update_geometry() -> None:
    finger.pos = vector(state["finger_x"], state["finger_height"], 0)
    finger.radius = state["finger_radius"]


def refresh_field() -> None:
    # Remove old arrows
    while field_arrows:
        obj = field_arrows.pop()
        obj.visible = False

    # Sample points above and around the electrode
    x_points = [
        -6.5, -5.5, -4.5, -3.5, -2.5, -1.5, -0.5,
        0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5,
    ]
    y_points = [0.5, 1.1, 1.7, 2.3, 2.9, 3.5, 4.1, 4.7, 5.3]

    for y in y_points:
        for x in x_points:
            p = vector(x, y, 0)
            e = electric_field_at(p)
            mag = e.mag

            if not isfinite(mag) or mag <= 1e-8:
                axis = vector(0, 0, 0)
            else:
                direction = e / mag
                length = 0.35 + 0.9 * clip(mag, 0, 1.8)
                axis = direction * length

            a = arrow(
                pos=p,
                axis=axis,
                color=color.white,
                shaftwidth=0.055,
                opacity=0.95,
                round=True,
            )
            field_arrows.append(a)


def redraw() -> None:
    update_geometry()
    update_labels()
    refresh_field()


def on_height_change(s: slider) -> None:
    state["finger_height"] = s.value
    redraw()


def on_x_change(s: slider) -> None:
    state["finger_x"] = s.value
    redraw()


def on_radius_change(s: slider) -> None:
    state["finger_radius"] = s.value
    redraw()


def on_voltage_change(s: slider) -> None:
    state["drive_voltage"] = s.value
    redraw()


# UI controls
scene.append_to_caption("\nControls\n")
scene.append_to_caption("Move the finger and watch the fringing field change.\n\n")

scene.append_to_caption("Finger left-right position")
x_slider = slider(min=-5.0, max=5.0, value=state["finger_x"], length=320, bind=on_x_change)
scene.append_to_caption(" value:")
x_text = wtext(text="")
scene.append_to_caption("\n")

scene.append_to_caption("Finger distance from electrode")
height_slider = slider(min=0.6, max=6.0, value=state["finger_height"], length=320, bind=on_height_change)
scene.append_to_caption(" value:")
height_text = wtext(text="")
scene.append_to_caption("\n")

scene.append_to_caption("Finger size")
radius_slider = slider(min=0.5, max=2.5, value=state["finger_radius"], length=320, bind=on_radius_change)
scene.append_to_caption(" value:")
radius_text = wtext(text="")
scene.append_to_caption("\n")

scene.append_to_caption("Electrode drive voltage")
voltage_slider = slider(min=0.2, max=2.5, value=state["drive_voltage"], length=320, bind=on_voltage_change)
scene.append_to_caption(" value:")
voltage_text = wtext(text="")
scene.append_to_caption("\n")

scene.append_to_caption("\n")
info = wtext(text="")

update_labels()
redraw()

# Keep application responsive
while True:
    rate(30)
