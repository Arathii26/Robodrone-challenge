"""Drone Flight Training Simulator  (Python + Ursina)"""
import math, random
from ursina import *

app = Ursina(title="Drone Flight Training Simulator", borderless=False)
random.seed(11)
window.exit_button.visible = False

# ---------- constants ----------
G = 9.81
HOVER = 0.5
MAX_TILT = 32
CRASH_SPEED = 4.5
CRASH_TILT = 15
SKY = color.hsv(205, .35, .95)

def C(h, s, v): return color.hsv(h, s, v)

scene.fog_color = SKY
scene.fog_density = (70, 300)
window.color = SKY
camera.fov = 85
Sky(color=SKY)

# ---------- world ----------
ground = Entity(model='plane', scale=600, color=C(120, .45, .42),
                texture='white_cube', texture_scale=(300, 300))
# runway-style roads
Entity(model='cube', scale=(6, .03, 600), position=(0, .01, 0), color=C(0, 0, .25))
Entity(model='cube', scale=(600, .03, 6), position=(0, .01, 0), color=C(0, 0, .25))

PADS = [("HOME", Vec3(0, 0, 0), color.yellow), ("PAD B", Vec3(55, 0, 40), color.cyan)]
for name, p, col in PADS:
    Entity(model='cube', position=p + Vec3(0, .06, 0), scale=(8, .1, 8), color=C(0, 0, .15))
    Entity(model='sphere', position=p + Vec3(0, .13, 0), scale=(6.6, .05, 6.6), color=col)
    Entity(model='sphere', position=p + Vec3(0, .15, 0), scale=(5.4, .05, 5.4), color=C(0, 0, .15))
    Text(text=name, parent=scene, position=p + Vec3(-1, 6, 0), scale=18, color=col, billboard=True)

buildings = []
tries = 0
while len(buildings) < 32 and tries < 500:
    tries += 1
    x, z = random.uniform(-110, 110), random.uniform(-110, 110)
    if abs(x) < 8 or abs(z) < 8:                       # keep roads clear
        continue
    if any(distance_2d(Vec3(x, 0, z), p) < 16 for _, p, _ in PADS):
        continue
    w, d, h = random.uniform(6, 12), random.uniform(6, 12), random.uniform(10, 38)
    if any(abs(x - c.x) < hs.x + w / 2 + 3 and abs(z - c.z) < hs.z + d / 2 + 3 for c, hs in buildings):
        continue
    tone = random.choice([(210, .25), (30, .2), (0, .0), (200, .35), (15, .3)])
    Entity(model='cube', position=(x, h / 2, z), scale=(w, h, d),
           color=C(tone[0], tone[1], random.uniform(.55, .85)),
           texture='white_cube', texture_scale=(w / 2, h / 2))
    Entity(model='cube', position=(x, h + .3, z), scale=(w + .5, .6, d + .5), color=C(0, 0, .25))
    buildings.append((Vec3(x, h / 2, z), Vec3(w / 2, h / 2, d / 2)))

def blocked(x, z, pad=4):
    return (any(abs(x - c.x) < hs.x + pad and abs(z - c.z) < hs.z + pad for c, hs in buildings)
            or abs(x) < 5 or abs(z) < 5
            or any(distance_2d(Vec3(x, 0, z), p) < 10 for _, p, _ in PADS))

for _ in range(70):                                     # trees
    x, z = random.uniform(-130, 130), random.uniform(-130, 130)
    if blocked(x, z):
        continue
    s = random.uniform(.8, 1.5)
    Entity(model='cube', position=(x, s, z), scale=(.5 * s, 2 * s, .5 * s), color=C(25, .6, .3))
    Entity(model='sphere', position=(x, 3.2 * s, z), scale=3.2 * s, color=C(random.randint(105, 140), .6, random.uniform(.4, .6)))

# clouds
for _ in range(14):
    cx, cz, cy = random.uniform(-200, 200), random.uniform(-200, 200), random.uniform(60, 90)
    for i in range(4):
        Entity(model='sphere', color=color.white, position=(cx + i * 6, cy + random.uniform(-1, 1), cz),
               scale=(random.uniform(9, 14), 4, random.uniform(7, 10)))

# rings
RING_COLS = [color.orange, color.magenta, color.azure]
rings = []
tries = 0
while len(rings) < 8 and tries < 500:
    tries += 1
    pos = Vec3(random.uniform(-70, 70), random.uniform(6, 20), random.uniform(-70, 70))
    if any(abs(pos.x - c.x) < hs.x + 6 and abs(pos.z - c.z) < hs.z + 6 and pos.y < c.y + hs.y + 6 for c, hs in buildings):
        continue
    if any(distance(pos, r["e"].position) < 20 for r in rings):
        continue
    e = Entity(position=pos, rotation_y=random.choice([0, 45, 90, 135]))
    parts = []
    for k in range(24):
        a = k * math.tau / 24
        parts.append(Entity(parent=e, model='cube', color=color.orange, scale=(.55, .55, .55),
                            position=(math.cos(a) * 3.5, math.sin(a) * 3.5, 0), rotation_z=math.degrees(a)))
    rings.append({"e": e, "parts": parts, "done": False})

# ---------- drone ----------
drone = Entity()                                        # root: position + yaw
body = Entity(parent=drone)                             # pitch + roll
Entity(parent=body, model='cube', color=C(220, .3, .25), scale=(.9, .22, 1.3))
Entity(parent=body, model='cube', color=C(0, 0, .1), scale=(.6, .28, .7), y=.1)
for rot in (45, -45):
    Entity(parent=body, model='cube', color=C(0, 0, .18), scale=(.12, .08, 2.6), rotation_y=rot)
props = []
for dx, dz in [(-.92, -.92), (.92, -.92), (-.92, .92), (.92, .92)]:
    Entity(parent=body, model='sphere', color=C(0, 0, .12), position=(dx, .05, dz), scale=.28)
    props.append(Entity(parent=body, model='cube', color=color.rgba(200, 200, 255, 140) if hasattr(color, 'rgba') else color.light_gray,
                        position=(dx, .22, dz), scale=(1.1, .02, .12)))
Entity(parent=body, model='sphere', color=color.lime, position=(0, 0, .7), scale=.15)
Entity(parent=body, model='sphere', color=color.red, position=(0, 0, -.7), scale=.15)
shadow = Entity(model='sphere', color=color.black, scale=(1.6, .02, 1.6))

# ---------- state ----------
S = {}
def reset():
    S.update(pos=Vec3(0, .1, 0), vel=Vec3(0, 0, 0), pitch=0.0, roll=0.0, yaw=0.0,
             throttle=0.0, crashed=False, score=0, msg="", msg_t=0, airborne=False,
             flight_t=0.0, started=False, won=False)
    for r in rings:
        r["done"] = False
        for p in r["parts"]: p.color = color.orange
reset()

# ---------- HUD ----------
panel = Entity(parent=camera.ui, model='quad', color=color.black66, scale=(.36, .25), position=(-.68, .36))
hud = Text(text="", position=(-.85, .46), scale=1.15, color=color.white)
thr_bg = Entity(parent=camera.ui, model='quad', color=color.dark_gray, scale=(.3, .022), position=(-.68, .27))
thr_bar = Entity(parent=camera.ui, model='quad', color=color.lime, origin=(-.5, 0), scale=(.001, .022), position=(-.83, .27))
banner = Text(text="", origin=(0, 0), position=(0, .18), scale=2.6, color=color.white)
toast = Text(text="", origin=(0, 0), position=(0, .10), scale=1.6, color=color.yellow)
cam_label = Text(text="", position=(.62, .47), scale=1.0, color=color.white)
help_t = Text(position=(-.85, .1), scale=.95, background=True,
    text="SPACE / SHIFT  throttle      W / S  pitch\nA / D  roll      Q / E  yaw\n"
         "R reset     C camera     H help     ESC quit\nHover throttle ~50%.  Fly through rings, land on pads!")
cam_mode = 0
CAMS = ["CHASE", "FPV", "ORBIT"]

def input(key):
    global cam_mode
    if key == 'r':
        reset(); banner.text = ""
    elif key == 'c':
        cam_mode = (cam_mode + 1) % 3
    elif key == 'h':
        help_t.enabled = not help_t.enabled
    elif key == 'escape':
        application.quit()

def approach(v, target, rate, dt):
    return v + max(-rate * dt, min(rate * dt, target - v))

def hits_building(p):
    for c, h in buildings:
        if abs(p.x - c.x) < h.x + .6 and abs(p.y - c.y) < h.y + .3 and abs(p.z - c.z) < h.z + .6:
            return True
    return False

def crash(text):
    S["crashed"] = True
    banner.text = text; banner.color = color.red
    for _ in range(24):
        e = Entity(model='cube', position=S["pos"], scale=random.uniform(.1, .3), color=random.choice([color.red, color.orange, color.dark_gray]))
        e.animate_position(S["pos"] + Vec3(random.uniform(-4, 4), random.uniform(.5, 4), random.uniform(-4, 4)),
                           duration=.9, curve=curve.out_expo)
        destroy(e, delay=2.5)

def say(t):
    S["msg"] = t; S["msg_t"] = 2.5

def update():
    dt = min(time.dt, 1 / 30)
    k = held_keys
    pos, vel = S["pos"], S["vel"]

    if not S["crashed"]:
        S["throttle"] = max(0, min(1, S["throttle"] + (k['space'] - k['left shift']) * .6 * dt))
        S["pitch"] = approach(S["pitch"], (k['w'] - k['s']) * MAX_TILT, 100, dt)
        S["roll"] = approach(S["roll"], (k['d'] - k['a']) * MAX_TILT, 100, dt)
        S["yaw"] += (k['e'] - k['q']) * 100 * dt

        p, r, y = map(math.radians, (S["pitch"], S["roll"], S["yaw"]))
        t = S["throttle"] * 2 * G
        fwd, right, up = math.sin(p), math.sin(r), math.cos(p) * math.cos(r)
        acc = Vec3((right * math.cos(y) + fwd * math.sin(y)) * t,
                   up * t - G,
                   (-right * math.sin(y) + fwd * math.cos(y)) * t)
        vel += acc * dt
        vel -= vel * .55 * dt                            # air drag
        new = pos + vel * dt

        if hits_building(new):
            crash("CRASH!  Hit a building  -  press R")
        elif new.y <= .1:
            impact = -vel.y
            tilt = max(abs(S["pitch"]), abs(S["roll"]))
            if impact > CRASH_SPEED or (tilt > CRASH_TILT and impact > 1.0):
                crash("CRASH!  Hard landing  -  press R")
            else:
                if S["airborne"] and impact > .3:
                    for name, pad, _ in PADS:
                        d = distance_2d(new, pad)
                        if d < 4:
                            pts = int(100 * (1 - d / 4)); S["score"] += pts
                            say(f"Landed on {name}!  +{pts}")
                            break
                    S["airborne"] = False
                vel = Vec3(vel.x * (1 - 4 * dt), max(vel.y, 0), vel.z * (1 - 4 * dt))
                new.y = .1
        else:
            if new.y > 2: S["airborne"] = True
            if new.y > .5: S["started"] = True
        S["pos"], S["vel"], pos = new, vel, new

        if S["started"] and not S["won"]:
            S["flight_t"] += dt
        for rg in rings:
            if not rg["done"] and distance(pos, rg["e"].position) < 3.2:
                rg["done"] = True; S["score"] += 50
                for pt in rg["parts"]: pt.color = color.lime
                say("Ring!  +50")
        if all(r["done"] for r in rings) and not S["won"]:
            S["won"] = True; S["score"] += 200
            banner.text = f"ALL RINGS!  {S['flight_t']:.1f}s   (+200)"; banner.color = color.lime

    # visuals
    drone.position = pos
    drone.rotation_y = S["yaw"]
    body.rotation_x = S["pitch"]; body.rotation_z = -S["roll"]
    spin = 2500 * (.2 + S["throttle"]) if not S["crashed"] else 0
    for pr in props: pr.rotation_y += spin * dt
    shadow.position = Vec3(pos.x, .05, pos.z)
    shadow.scale = (max(.4, 1.6 - pos.y * .04), .02, max(.4, 1.6 - pos.y * .04))
    for i, rg in enumerate(rings):
        if not rg["done"]:
            rg["e"].scale = 1 + .04 * math.sin(time.time() * 4 + i)

    # cameras
    yr = math.radians(S["yaw"]); f = Vec3(math.sin(yr), 0, math.cos(yr))
    if cam_mode == 0:
        target = pos - f * 9 + Vec3(0, 3.5, 0)
        camera.position = lerp(camera.position, target, min(1, 6 * dt))
        camera.look_at(pos + Vec3(0, 1, 0))
    elif cam_mode == 1:
        camera.position = pos + f * .7 + Vec3(0, .2, 0)
        camera.rotation = (S["pitch"], S["yaw"], -S["roll"])
    else:
        camera.position = pos + Vec3(0, 50, -35)
        camera.look_at(pos)
    if pos.y < .5 and cam_mode == 0 and camera.y < .5: camera.y = .5

    # HUD
    S["msg_t"] -= dt
    toast.text = S["msg"] if S["msg_t"] > 0 else ""
    left = [r for r in rings if not r["done"]]
    nxt = min((distance(pos, r["e"].position) for r in left), default=0)
    hud.text = (f"ALT   {pos.y:5.1f} m\nSPEED {vel.length()*3.6:5.1f} km/h\n"
                f"THR   {S['throttle']*100:3.0f} %\nSCORE {S['score']}\n"
                f"RINGS {8-len(left)}/8   NEXT {nxt:4.0f} m\nTIME  {S['flight_t']:5.1f} s")
    thr_bar.scale_x = max(.001, .3 * S["throttle"])
    thr_bar.color = color.lime if S["throttle"] < .7 else color.orange
    cam_label.text = f"CAM: {CAMS[cam_mode]}"

reset()
app.run()