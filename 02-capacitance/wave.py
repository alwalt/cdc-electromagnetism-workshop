import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from textwrap import fill


"""3D visualization of why a frozen light wave is not allowed.

This script shows two views of the same plane electromagnetic wave:
1. The lab frame, where the wave propagates at c.
2. A subluminal observer frame, transformed with the Lorentz formulas.

As the observer speed approaches c, the observed frequency and wavenumber
shrink toward zero, but there is no valid inertial frame with v = c.
That is the key physics point behind Einstein's thought experiment.
"""


c = 1.0
amplitude = 1.0
wavelength = 2.0
k = 2 * np.pi / wavelength
omega = c * k

# Set this anywhere in [0, 1). A true co-moving frame at v = c does not exist.
observer_speed = 0.9
show_field_vectors = False

if not 0.0 <= observer_speed < c:
    raise ValueError(
        "observer_speed must satisfy 0 <= v < c. "
        "A frozen light-wave frame at v = c is not allowed in special relativity."
    )


def lorentz_wave_numbers(v):
    """Return transformed wavenumber and angular frequency for motion along +x."""
    gamma = 1.0 / np.sqrt(1.0 - (v / c) ** 2)
    k_prime = gamma * (k - v * omega / (c**2))
    omega_prime = gamma * (omega - v * k)
    return k_prime, omega_prime, gamma


def field_components(x_values, t_value, k_value, omega_value):
    """Plane wave traveling along +x with E along y and B along z."""
    phase = k_value * x_values - omega_value * t_value
    e_field = amplitude * np.sin(phase)
    b_field = e_field / c
    return e_field, b_field


x = np.linspace(0.0, 8.0, 320)
k_prime, omega_prime, gamma = lorentz_wave_numbers(observer_speed)
lambda_prime = 2 * np.pi / k_prime if abs(k_prime) > 1e-12 else np.inf
frequency_prime = omega_prime / (2 * np.pi)

fig = plt.figure(figsize=(14, 7))
ax_lab = fig.add_subplot(121, projection="3d")
ax_obs = fig.add_subplot(122, projection="3d")

fig.suptitle("Why You Cannot Freeze a Light Wave", fontsize=16)


def setup_axes(axis, title):
    axis.set_xlim(0, 8)
    axis.set_ylim(-1.4, 1.4)
    axis.set_zlim(-1.4, 1.4)
    axis.set_xlabel("Propagation direction x")
    axis.set_ylabel("Electric field Ey")
    axis.set_zlabel("Magnetic field Bz")
    axis.set_title(title)
    axis.view_init(elev=24, azim=-64)


setup_axes(ax_lab, "Lab Frame: Valid Traveling Wave")
setup_axes(ax_obs, "Observer Frame: v < c Only")

line_lab_e, = ax_lab.plot([], [], [], color="dodgerblue", lw=2.6, label="E field")
line_lab_b, = ax_lab.plot([], [], [], color="tomato", lw=2.6, label="B field")
line_obs_e, = ax_obs.plot([], [], [], color="dodgerblue", lw=2.6, label="E field")
line_obs_b, = ax_obs.plot([], [], [], color="tomato", lw=2.6, label="B field")

sample_idx = np.linspace(0, len(x) - 1, 15, dtype=int)
lab_quiver = None
obs_quiver = None

ax_lab.legend(loc="upper right")
ax_obs.legend(loc="upper right")

lab_text = ax_lab.text2D(0.03, 0.95, "", transform=ax_lab.transAxes)
obs_text = ax_obs.text2D(0.03, 0.95, "", transform=ax_obs.transAxes)
left_note = ax_lab.text2D(
    0.03,
    0.04,
    "Left: lab frame. The wave moves at c and keeps its usual wavelength and frequency.",
    transform=ax_lab.transAxes,
    fontsize=9,
)
right_note = ax_obs.text2D(
    0.03,
    0.04,
    "Right: moving observer frame. The wave is still valid, but its oscillation is slowed by the Lorentz transform.",
    transform=ax_obs.transAxes,
    fontsize=9,
)
bottom_text = fig.text(0.06, 0.045, "", fontsize=10, va="bottom")


def make_quiver(axis, x_values, e_values, b_values):
    return axis.quiver(
        x_values,
        np.zeros_like(x_values),
        np.zeros_like(x_values),
        np.zeros_like(x_values),
        e_values,
        b_values,
        length=0.6,
        normalize=False,
        color="gray",
        alpha=0.55,
        linewidths=1.0,
    )


def update(frame):
    global lab_quiver, obs_quiver

    t_lab = frame * 0.04
    t_obs = t_lab / gamma

    e_lab, b_lab = field_components(x, t_lab, k, omega)
    e_obs, b_obs = field_components(x, t_obs, k_prime, omega_prime)

    line_lab_e.set_data_3d(x, e_lab, np.zeros_like(x))
    line_lab_b.set_data_3d(x, np.zeros_like(x), b_lab)

    line_obs_e.set_data_3d(x, e_obs, np.zeros_like(x))
    line_obs_b.set_data_3d(x, np.zeros_like(x), b_obs)

    if lab_quiver is not None:
        lab_quiver.remove()
        lab_quiver = None
    if obs_quiver is not None:
        obs_quiver.remove()
        obs_quiver = None

    if show_field_vectors:
        lab_quiver = make_quiver(ax_lab, x[sample_idx], e_lab[sample_idx], b_lab[sample_idx])
        obs_quiver = make_quiver(ax_obs, x[sample_idx], e_obs[sample_idx], b_obs[sample_idx])

    lab_text.set_text(
        f"c = {c:.1f}\n"
        f"lambda = {wavelength:.2f}\n"
        f"f = {omega / (2 * np.pi):.2f}"
    )
    obs_text.set_text(
        f"observer speed = {observer_speed:.2f} c\n"
        f"gamma = {gamma:.2f}\n"
        f"lambda' = {lambda_prime:.2f}\n"
        f"f' = {frequency_prime:.2f}"
    )

    bottom_text.set_text(
        fill(
            "Maxwell + relativity: as v approaches c, the observed oscillation slows, but a truly frozen wave would require v = c, which is not a valid inertial frame. If you force dE/dt = dB/dt = 0 in vacuum, the wave-regeneration mechanism disappears.",
            width=120,
        )
    )

    return (
        line_lab_e,
        line_lab_b,
        line_obs_e,
        line_obs_b,
        lab_text,
        obs_text,
        left_note,
        right_note,
        bottom_text,
    )


ani = FuncAnimation(fig, update, frames=320, interval=35, blit=False)
plt.tight_layout(rect=[0, 0.12, 1, 0.95])
plt.show()