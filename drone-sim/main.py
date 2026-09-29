from ursina import *


class Drone(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.azure,
            scale=(1.2, 0.3, 1.5),
            position=(0, 2, 0),
        )

        self.velocity = Vec3(0, 0, 0)
        self.throttle = 50.0
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        self.ground_level = 0.7

        self.body = Entity(parent=self, model='cube', color=color.azure, scale=(1.0, 0.2, 1.2), y=0.05)
        self.cabin = Entity(parent=self, model='cube', color=color.orange, scale=(0.55, 0.18, 0.55), y=0.2)

        arm_positions = [
            (-1, 0, 1),
            (1, 0, 1),
            (-1, 0, -1),
            (1, 0, -1),
        ]
        for x, y, z in arm_positions:
            Entity(parent=self, model='cube', color=color.gray, position=(x * 0.7, y, z * 0.7), scale=(0.12, 0.08, 1.2))
            Entity(parent=self, model='cube', color=color.black, position=(x * 0.7, 0.18, z * 0.7), scale=(0.45, 0.08, 0.45))

        self.hud = Text(
            text='',
            position=(-0.85, 0.45),
            scale=1.1,
            background=True,
            origin=(0, 0),
        )

    def input(self, key):
        if key == 'r':
            self.reset_drone()
        if key == 'escape':
            application.quit()

    def reset_drone(self):
        self.position = Vec3(0, 2, 0)
        self.velocity = Vec3(0, 0, 0)
        self.throttle = 50.0
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0

    def update(self):
        dt = time.dt

        if held_keys['space']:
            self.throttle += 28.0 * dt
        if held_keys['left shift']:
            self.throttle -= 28.0 * dt
        self.throttle = clamp(self.throttle, 0.0, 100.0)

        if held_keys['w']:
            self.pitch += 48.0 * dt
        if held_keys['s']:
            self.pitch -= 48.0 * dt
        if held_keys['a']:
            self.roll -= 48.0 * dt
        if held_keys['d']:
            self.roll += 48.0 * dt
        if held_keys['q']:
            self.yaw += 54.0 * dt
        if held_keys['e']:
            self.yaw -= 54.0 * dt

        self.pitch = clamp(self.pitch, -45.0, 45.0)
        self.roll = clamp(self.roll, -45.0, 45.0)

        self.rotation_x = self.pitch
        self.rotation_y = self.yaw
        self.rotation_z = self.roll

        lift_force = (self.throttle / 100.0) * 20.0
        gravity_force = Vec3(0, -9.81, 0)
        thrust_force = self.up * lift_force
        self.velocity += (thrust_force + gravity_force) * dt

        if abs(self.pitch) < 5.0 and abs(self.roll) < 5.0:
            drag = max(0.0, 1.0 - 2.5 * dt)
            self.velocity.x *= drag
            self.velocity.z *= drag

        self.position += self.velocity * dt

        if self.position.y < self.ground_level:
            self.position.y = self.ground_level
            if self.velocity.y < 0:
                self.velocity.y = 0.0

        self.update_hud()

    def update_hud(self):
        altitude = max(0.0, self.position.y - self.ground_level)
        speed = self.velocity.length()
        self.hud.text = f'Altitude: {altitude:.1f} m\nSpeed: {speed:.1f} m/s\nThrottle: {self.throttle:.0f}%'


app = Ursina()
window.title = 'Drone Flight Training Simulator'
window.borderless = False
window.color = color.rgb(145, 170, 200)
window.exit_button.enabled = False

camera.position = (0, 7, -18)
camera.rotation_x = 20

DirectionalLight(parent=camera, y=10, z=10, rotation=(45, -30, 0))
AmbientLight(color=color.rgba(180, 180, 180, 120))

Entity(model='plane', scale=(80, 1, 80), color=color.rgb(20, 120, 40), rotation_x=90, y=0)
Drone()

app.run()
