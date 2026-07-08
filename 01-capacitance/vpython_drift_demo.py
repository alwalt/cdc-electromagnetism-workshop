"""Standalone VPython demo: fast random electron motion + slow net drift.

Run:
    python3 vpython_drift_demo.py

If imports fail, install into your active environment:
    python3 -m pip install -U vpython
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np


try:
    from vpython import (
        arrow,
        button,
        canvas,
        color,
        cylinder,
        rate,
        slider,
        sphere,
        vector,
        wtext,
    )
except Exception as exc:
    raise SystemExit(
        "VPython import failed. In this same terminal, run:\n"
        "  python3 -m pip install -U vpython\n"
        f"Original error: {exc}"
    )


@dataclass
class SimParams:
    drift_bias: float = 0.010
    random_kick: float = 0.080
    damping: float = 0.960
    dt: float = 0.040


class DriftSimulation:
    def __init__(self) -> None:
        self.params = SimParams()
        self.running = True

        self.wire_length = 10.0
        self.wire_radius = 1.2
        self.n_particles = 120
        self.radius_e = 0.075

        self.scene = canvas(
            title="Electron Motion: Fast Random + Slow Drift",
            width=1100,
            height=650,
            background=vector(0.06, 0.07, 0.10),
        )
        self.scene.forward = vector(-1.0, -0.25, -0.65)
        self.scene.range = 7

        self._build_scene()
        self._build_controls()
        self._spawn_particles()

    def _build_scene(self) -> None:
        self.wire = cylinder(
            pos=vector(-self.wire_length / 2, 0, 0),
            axis=vector(self.wire_length, 0, 0),
            radius=self.wire_radius,
            color=vector(0.45, 0.52, 0.65),
            opacity=0.23,
        )

        self.drift_arrow = arrow(
            pos=vector(-self.wire_length / 2 - 1.6, self.wire_radius + 0.95, 0),
            axis=vector(2.2, 0, 0),
            shaftwidth=0.16,
            color=color.orange,
        )

    def _build_controls(self) -> None:
        self.scene.append_to_caption("\nControls\n")

        self.scene.append_to_caption("Drift bias   ")
        self.drift_slider = slider(
            min=0.000,
            max=0.040,
            value=self.params.drift_bias,
            step=0.001,
            bind=self._on_slider_change,
        )

        self.scene.append_to_caption("\nRandom kick  ")
        self.kick_slider = slider(
            min=0.010,
            max=0.200,
            value=self.params.random_kick,
            step=0.005,
            bind=self._on_slider_change,
        )

        self.scene.append_to_caption("\nDamping      ")
        self.damp_slider = slider(
            min=0.850,
            max=0.999,
            value=self.params.damping,
            step=0.001,
            bind=self._on_slider_change,
        )

        self.scene.append_to_caption("\ndt           ")
        self.dt_slider = slider(
            min=0.010,
            max=0.120,
            value=self.params.dt,
            step=0.005,
            bind=self._on_slider_change,
        )

        self.scene.append_to_caption("\n\n")
        self.toggle_btn = button(text="Pause", bind=self._toggle_running)
        self.scene.append_to_caption("   ")
        button(text="Reset", bind=self._reset_particles)
        self.scene.append_to_caption("\n\n")
        self.status = wtext(text="")

    def _spawn_particles(self) -> None:
        self.particles = []
        self.velocities = []
        for _ in range(self.n_particles):
            r = self.wire_radius * np.sqrt(random.random())
            theta = 2 * np.pi * random.random()
            y = r * np.cos(theta)
            z = r * np.sin(theta)
            x = random.uniform(-self.wire_length / 2, self.wire_length / 2)

            particle = sphere(
                pos=vector(x, y, z),
                radius=self.radius_e,
                color=vector(0.30, 0.82, 1.00),
                shininess=0.2,
                make_trail=False,
            )
            self.particles.append(particle)
            self.velocities.append(
                vector(
                    random.uniform(-0.2, 0.2),
                    random.uniform(-0.2, 0.2),
                    random.uniform(-0.2, 0.2),
                )
            )

    def _toggle_running(self, _evt) -> None:
        self.running = not self.running
        self.toggle_btn.text = "Pause" if self.running else "Resume"

    def _on_slider_change(self, _evt) -> None:
        self._sync_params()

    def _reset_particles(self, _evt) -> None:
        for particle in self.particles:
            particle.visible = False
        self._spawn_particles()

    def _sync_params(self) -> None:
        self.params.drift_bias = self.drift_slider.value
        self.params.random_kick = self.kick_slider.value
        self.params.damping = self.damp_slider.value
        self.params.dt = self.dt_slider.value

    def _step(self) -> float:
        p = self.params
        sum_vx = 0.0

        for i, particle in enumerate(self.particles):
            kick = vector(
                random.uniform(-p.random_kick, p.random_kick),
                random.uniform(-p.random_kick, p.random_kick),
                random.uniform(-p.random_kick, p.random_kick),
            )
            self.velocities[i] = p.damping * self.velocities[i] + kick + vector(p.drift_bias, 0, 0)
            particle.pos += self.velocities[i] * p.dt

            if particle.pos.x > self.wire_length / 2:
                particle.pos.x -= self.wire_length
            elif particle.pos.x < -self.wire_length / 2:
                particle.pos.x += self.wire_length

            rho = np.sqrt(particle.pos.y**2 + particle.pos.z**2)
            if rho > (self.wire_radius - self.radius_e):
                scale = (self.wire_radius - self.radius_e) / rho
                particle.pos.y *= scale
                particle.pos.z *= scale

                normal = vector(0, particle.pos.y, particle.pos.z)
                if normal.mag > 0:
                    normal = normal.norm()
                    self.velocities[i] = self.velocities[i] - 2 * self.velocities[i].dot(normal) * normal

            sum_vx += self.velocities[i].x

        return sum_vx / self.n_particles

    def run(self) -> None:
        step_count = 0
        while True:
            rate(120)
            self._sync_params()

            if self.running:
                mean_vx = self._step()
                self.drift_arrow.axis = vector(2.0 + 80 * mean_vx, 0, 0)
            else:
                mean_vx = 0.0

            if step_count % 10 == 0:
                self.status.text = (
                    f"Mean vx: {mean_vx:+.4f}  |  "
                    f"drift_bias={self.params.drift_bias:.3f}, "
                    f"random_kick={self.params.random_kick:.3f}, "
                    f"damping={self.params.damping:.3f}, dt={self.params.dt:.3f}"
                )
            step_count += 1


def main() -> int:
    sim = DriftSimulation()
    sim.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
