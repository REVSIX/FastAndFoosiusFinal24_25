import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
import time

# --- Constants ---
table_width, table_height = 800, 480
rod_x_asymptote_pixels = [595, 373, 147, 36]
player_counts = [3, 5, 2, 3]  # per rod
player_radius = 20
v_stepper = 0.07
min_rod_y, max_rod_y = player_radius / table_height, 1 - player_radius / table_height

# --- PID Controller ---
class SimplePID:
    def __init__(self, kp, ki, kd, out_min=-1, out_max=1):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.out_min = out_min
        self.out_max = out_max
        self.integral = 0
        self.prev_err = 0

    def update(self, target, current, dt):
        err = target - current
        self.integral += err * dt
        derivative = (err - self.prev_err) / dt if dt > 0 else 0
        output = (self.kp * err) + (self.ki * self.integral) + (self.kd * derivative)
        self.prev_err = err
        return max(self.out_min, min(self.out_max, output))

# --- Setup Graphics ---
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title("Realistic Foosball Defense Simulation (PID)")
ax.set_xlim(0, table_width)
ax.set_ylim(0, table_height)
ax.set_aspect('equal')
ax.set_facecolor("forestgreen")
ax.invert_yaxis()
ax.add_patch(plt.Rectangle((0, 0), table_width, table_height, edgecolor='white', lw=3, facecolor='none'))

# Rod graphics state
rod_positions = [0.5] * 4
rod_targets = [0.5] * 4
rod_lines = [ax.plot([x, x], [0, table_height], color='white', lw=3)[0] for x in rod_x_asymptote_pixels]

# Ball setup
ball = Circle((table_width / 2, table_height / 2), radius=10, color='white')
ax.add_patch(ball)
state_text = ax.text(10, 20, "State: IDLE", fontsize=12, color="white")

# Player heads per rod
rod_players = []
for rod_index, x in enumerate(rod_x_asymptote_pixels):
    patches = []
    for i in range(player_counts[rod_index]):
        circle = Circle((x, 0), radius=player_radius, edgecolor='yellow', facecolor='black', lw=1)
        ax.add_patch(circle)
        patches.append(circle)
    rod_players.append(patches)

# Dragging state
drag_data = {"x": None, "y": None, "vx": 0, "vy": 0, "last_time": time.time()}

# PID setup
pid_gains = [(1, 0, 0)] * 4
rod_pids = [SimplePID(*g, out_min=-v_stepper, out_max=v_stepper) for g in pid_gains]
rod_last_time = [time.time()] * 4

# Normalize Y position to [0, 1]
def normalize_y(y):
    return (y - 0) / (table_height - 0)

def clamp(val, min_val, max_val):
    return max(min(val, max_val), min_val)

# Mouse events
def on_press(event):
    if ball.contains(event)[0]:
        drag_data.update(x=event.xdata, y=event.ydata, last_time=time.time())

def on_release(event):
    drag_data["x"] = None
    drag_data["y"] = None

def on_motion(event):
    if drag_data["x"] is None or event.xdata is None or event.ydata is None:
        return

    dt = time.time() - drag_data["last_time"]
    dx = event.xdata - drag_data["x"]
    dy = event.ydata - drag_data["y"]
    vx = dx / dt if dt > 0 else 0
    vy = dy / dt if dt > 0 else 0
    drag_data.update(x=event.xdata, y=event.ydata, vx=vx, vy=vy, last_time=time.time())
    ball.set_center((event.xdata, event.ydata))

    x_final = np.array(rod_x_asymptote_pixels)
    y2 = event.ydata
    y_final = y2 + vy * (x_final - event.xdata) / vx if vx != 0 else np.full_like(x_final, y2)

    for rod_index, y_target in enumerate(y_final):
        y_norm = clamp(normalize_y(y_target), min_rod_y, max_rod_y)
        rod_targets[rod_index] = y_norm

# Player update
def get_closest_player_index(rod_index, y_cross, rod_positions):
    n_players = player_counts[rod_index]
    total_span = table_height - 2 * player_radius
    spacing = total_span / (n_players + 1)
    center_y = rod_positions[rod_index] * table_height
    player_ys = [center_y + (i - (n_players - 1) / 2) * spacing for i in range(n_players)]
    closest_idx = np.argmin([abs(y - y_cross) for y in player_ys])
    return closest_idx, player_ys

def update_player_positions():
    ball_x, ball_y = ball.center
    vx, vy = drag_data["vx"], drag_data["vy"]
    for rod_index, x in enumerate(rod_x_asymptote_pixels):
        patches = rod_players[rod_index]
        n_players = len(patches)
        rod_x = rod_x_asymptote_pixels[rod_index]
        # Predict where ball will cross this rod
        if vx != 0:
            y_cross = ball_y + vy * (rod_x - ball_x) / vx
        else:
            y_cross = ball_y
        y_cross = clamp(y_cross, player_radius, table_height - player_radius)
        # Calculate player ranges
        total_span = table_height - 2 * player_radius
        spacing = total_span / (n_players + 1)
        player_centers = [player_radius + (i + 1) * spacing for i in range(n_players)]
        # Find which player is closest to y_cross
        distances = [abs(y_cross - pc) for pc in player_centers]
        intercept_idx = np.argmin(distances)
        # Calculate offset needed to move intercepting player to y_cross
        offset = y_cross - player_centers[intercept_idx]
        # Clamp offset so no player goes out of bounds
        min_offset = player_radius - min(player_centers)
        max_offset = (table_height - player_radius) - max(player_centers)
        offset = clamp(offset, min_offset, max_offset)
        # Apply offset to all players
        new_positions = [pc + offset for pc in player_centers]
        # Log data for debugging
        print(f"Rod {rod_index}: n_players={n_players}, y_cross={y_cross:.2f}, intercept_idx={intercept_idx}, offset={offset:.2f}, player_centers={player_centers}, new_positions={new_positions}")
        # Set positions
        for i, patch in enumerate(patches):
            patch.center = (x, new_positions[i])

# Animate
def animate(frame):
    now = time.time()
    for i in range(4):
        dt = now - rod_last_time[i]
        rod_last_time[i] = now
        step = rod_pids[i].update(rod_targets[i], rod_positions[i], dt)
        rod_positions[i] = clamp(rod_positions[i] + step, min_rod_y, max_rod_y)

    update_player_positions()

    targets_disp = ", ".join(f"{rod_targets[i]:.2f}" for i in range(4))
    positions_disp = ", ".join(f"{rod_positions[i]:.2f}" for i in range(4))
    state_text.set_text(
        f"Rods P: [{positions_disp}]\nRods T: [{targets_disp}]"
    )

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('motion_notify_event', on_motion)

ani = FuncAnimation(fig, animate, interval=20)
plt.show()