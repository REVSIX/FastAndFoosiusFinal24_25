import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.animation import FuncAnimation
import time

# --- Constants ---
table_width, table_height = 800, 480
rod_x_asymptote_pixels = [595, 373, 147, 36]
player_areas_per_rod_pixels = [
    [(19, 112), (112, 206), (206, 297)],             # Rod 0 (Offense)
    [(17, 68), (80, 131), (142, 192), (202, 251), (264, 313)],  # Rod 1 (Midfield)
    [(18, 185), (146, 311)],                         # Rod 2 (Defense)
    [(23, 127), (117, 220), (211, 314)],             # Rod 3 (Goalie)
]
v_stepper = 0.07          # max normalized step per frame (tightly modeled for realism)
intercept_threshold = 0.25  # time window, in seconds, to respond

# --- PID Controller Class ---
class SimplePID:
    def __init__(self, kp, ki, kd, out_min=-1, out_max=1):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.out_min = out_min
        self.out_max = out_max
        self.integral = 0
        self.prev_err = 0

    def reset(self):
        self.integral = 0
        self.prev_err = 0

    def update(self, target, current, dt):
        err = target - current
        self.integral += err * dt
        derivative = (err - self.prev_err) / dt if dt > 0 else 0
        output = (self.kp * err) + (self.ki * self.integral) + (self.kd * derivative)
        self.prev_err = err
        return max(self.out_min, min(self.out_max, output))

# --- State Machine ---
class FoosballStateMachine:
    def __init__(self):
        self.state = "IDLE"
        self.controlled_rod = None
        self.controlled_player = None

    def update(self, x, y, vx, vy, x_final, y_final):
        if self.state == "IDLE":
            if abs(vx) > 0.5:
                self.state = "TRACKING"
        elif self.state == "TRACKING":
            rod_idx, player_idx = self.get_intercept_player(y_final, vy)
            if rod_idx is not None:
                self.controlled_rod = rod_idx
                self.controlled_player = player_idx
                self.state = "TRAPPING"
        elif self.state == "TRAPPING":
            if abs(vx) < 0.5:
                self.state = "IDLE"

    def get_intercept_player(self, y_final, vy):
        for rod_index, players in enumerate(player_areas_per_rod_pixels):
            for player_index, (start, end) in enumerate(players):
                if start <= y_final[rod_index] <= end:
                    return rod_index, player_index
        return None, None

    def has_control_of_ball(self, y):
        return 0 <= y <= 470

# --- Prediction Function ---
def predict_final_position(x1, y1, x2, y2, time_diff):
    vx = (x2 - x1) / time_diff if time_diff > 0 else 0
    vy = (y2 - y1) / time_diff if time_diff > 0 else 0
    x_final = np.array(rod_x_asymptote_pixels)
    y_final = y2 + vy * (x_final - x2) / vx if vx != 0 else np.full_like(x_final, y2)
    return x_final, y_final, vx, vy

def normalize_y(y, top=0, bottom=table_height):
    return (y - top) / (bottom - top)

def clamp(val, min_val, max_val):
    return max(min(val, max_val), min_val)

# --- Setup Graphics ---
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title("Realistic Foosball Defense Simulation (PID)")
ax.set_xlim(0, table_width)
ax.set_ylim(0, table_height)
ax.set_aspect('equal')
ax.set_facecolor("forestgreen")
ax.invert_yaxis()

ax.add_patch(Rectangle((0, 0), table_width, table_height, edgecolor='white', lw=3, facecolor='none'))

# Rod graphics state
rod_positions = [0.5] * 4  # normalized y, each rod
rod_targets = [0.5] * 4    # (where PID wants rod center to be)
rod_lines = [ax.plot([x, x], [0, table_height], color='white', lw=3)[0] for x in rod_x_asymptote_pixels]

# Ball setup
ball = Circle((table_width / 2, table_height / 2), radius=10, color='white')
ax.add_patch(ball)
state_text = ax.text(10, 20, "State: IDLE", fontsize=12, color="white")

# Player rectangles per rod
rod_players = []
for rod_index, x in enumerate(rod_x_asymptote_pixels):
    patches = []
    for (start, end) in player_areas_per_rod_pixels[rod_index]:
        rect = Rectangle((x - 15, start), 30, end - start, edgecolor='yellow', facecolor='black', lw=1)
        ax.add_patch(rect)
        patches.append(rect)
    rod_players.append(patches)

state_machine = FoosballStateMachine()
drag_data = {"x": None, "y": None, "vx": 0, "vy": 0, "last_time": time.time()}

# --- PID Controllers per Rod ---
pid_gains = [
    (1, 0, 0),  # Rod 0: Offense
    (1, 0, 0),  # Rod 1: Midfield
    (1, 0, 0),  # Rod 2: Defense
    (1, 0, 0),  # Rod 3: Goalie
]
rod_pids = [SimplePID(*g, out_min=-v_stepper, out_max=v_stepper) for g in pid_gains]
rod_last_time = [time.time()] * 4

# --- Mouse Event Handling ---
def on_press(event):
    if ball.contains(event)[0]:
        drag_data["x"] = event.xdata
        drag_data["y"] = event.ydata
        drag_data["last_time"] = time.time()

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

    # Predict trajectory to each rod
    x_final, y_final, vx, vy = predict_final_position(
        event.xdata - dx, event.ydata - dy, event.xdata, event.ydata, dt
    )
    state_machine.update(event.xdata, event.ydata, vx, vy, x_final, y_final)
    state_text.set_text(
        f"Robot State: {state_machine.state}\n"
        + "Rod ctrl: {} | Target: {}".format(
            state_machine.controlled_rod, state_machine.controlled_player)
    )

    # Set rod targets to predicted ball Y on each rod if feasible
    for rod_index, x_rod in enumerate(rod_x_asymptote_pixels):
        time_to_intercept = abs((x_rod - event.xdata) / vx) if vx != 0 else float('inf')
        for player_index, (start, end) in enumerate(player_areas_per_rod_pixels[rod_index]):
            y_target = y_final[rod_index]
            if start <= y_target <= end:
                # Clamp normalized position to rod's allowed zone [0,1]
                normalized_target = clamp(normalize_y(y_target), 0, 1)
                rod_targets[rod_index] = normalized_target

# --- Update Player Positions ---
def update_player_positions():
    for rod_index, x in enumerate(rod_x_asymptote_pixels):
        patches = rod_players[rod_index]
        for p_index, (start, end) in enumerate(player_areas_per_rod_pixels[rod_index]):
            # Adjusting player size (height of the black box)
            y_len = end - start
            y_center = rod_positions[rod_index] * table_height
            # Update each player's y-position based on rod position
            player_rect = patches[p_index]
            player_rect.set_height(y_len * 0.8)  # Make the player boxes a little smaller (scale by 0.8)
            player_rect.set_y(y_center - player_rect.get_height() / 2 + (p_index - len(patches) / 2) * (y_len + 10))

# --- Updated Animation Loop ---
def animate(frame):
    now = time.time()
    # PID controlled rod movement
    for i in range(4):
        dt = now - rod_last_time[i]
        rod_last_time[i] = now
        step = rod_pids[i].update(rod_targets[i], rod_positions[i], dt)
        rod_positions[i] += step
        rod_positions[i] = clamp(rod_positions[i], 0, 1)

    # Visually move rod rectangles and update player positions
    update_player_positions()  # Ensure the players stay properly sized and positioned

    # Update state text
    targets_disp = ", ".join(f"{rod_targets[i]:.2f}" for i in range(4))
    positions_disp = ", ".join(f"{rod_positions[i]:.2f}" for i in range(4))
    state_text.set_text(
        f"Robot State: {state_machine.state}\n"
        + f"Rods P: [{positions_disp}]\n"
        + f"Rods T: [{targets_disp}]"
    )

# --- Event Bindings ---
fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('motion_notify_event', on_motion)

# --- Run Animation ---
ani = FuncAnimation(fig, animate, interval=30)
plt.show()
