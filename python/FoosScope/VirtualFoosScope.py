import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
import time
random_path = {"active": False, "start": None, "end": None, "speed": 0, "direction": None, "t": 0, "length": 0}

# --- Constants ---
table_width, table_height = 800, 480
rod_x_asymptote_pixels = [595, 373, 147, 36]
player_counts = [3, 5, 2, 3]  # per rod
player_radius = 20
v_stepper = 0.05  # Slower movement (was 0.07)
BALL_SPEED_FACTOR = 1  # Much slower ball
BALL_BOUNCE_FACTOR = 0.7  # Ball bounces with more energy
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
fig.canvas.manager.set_window_title("FoosScope - Realistic Foosball Simulation")
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
ball = Circle((500, 200), radius=10, color='white')
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

# --- Ball windup state ---
ball_windup = {"active": False, "start_x": None, "start_y": None, "vx": 0, "vy": 0}

# Mouse events
def on_press(event):
    if ball.contains(event)[0]:
        drag_data.update(x=event.xdata, y=event.ydata, last_time=time.time())
        ball_windup["active"] = True
        ball_windup["start_x"] = event.xdata
        ball_windup["start_y"] = event.ydata
        ball_windup["vx"] = 0
        ball_windup["vy"] = 0
        drag_data["vx"] = 0
        drag_data["vy"] = 0


def on_release(event):
    drag_data["x"] = None
    drag_data["y"] = None
    if ball_windup["active"]:
        # Calculate windup velocity only if mouse was dragged a significant distance
        dx = event.xdata - ball_windup["start_x"] if event.xdata is not None else 0
        dy = event.ydata - ball_windup["start_y"] if event.ydata is not None else 0
        dist = np.hypot(dx, dy)
        if dist > 10:  # Only wind up if drag is significant
            ball_windup["vx"] = dx * 0.2
            ball_windup["vy"] = dy * 0.2
            drag_data["vx"] = ball_windup["vx"]
            drag_data["vy"] = ball_windup["vy"]
        else:
            drag_data["vx"] = 0
            drag_data["vy"] = 0
        ball_windup["active"] = False

def on_motion(event):
    if drag_data["x"] is None or event.xdata is None or event.ydata is None:
        return
    # Only update ball position if windup is active
    if ball_windup["active"]:
        ball.set_center((event.xdata, event.ydata))
        drag_data["x"] = event.xdata
        drag_data["y"] = event.ydata
        drag_data["last_time"] = time.time()
        # Use zero velocity while dragging
        vx, vy = 0, 0
    else:
        # Use last known velocities from drag_data
        vx, vy = drag_data["vx"], drag_data["vy"]
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
        # Calculate player centers
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
        # Smoothly move the rod: interpolate current positions toward new positions
        current_positions = [patch.center[1] for patch in patches]
        target_positions = [pc + offset for pc in player_centers]
        move_speed = 0.08  # fraction of distance to move per frame (tune for smoothness)
        new_positions = [cur + move_speed * (tgt - cur) for cur, tgt in zip(current_positions, target_positions)]
        # Log data for debugging
        print(f"Rod {rod_index}: n_players={n_players}, y_cross={y_cross:.2f}, intercept_idx={intercept_idx}, offset={offset:.2f}, player_centers={player_centers}, target_positions={target_positions}, new_positions={new_positions}")
        # Set positions
        for i, patch in enumerate(patches):
            patch.center = (x, new_positions[i])

def detect_ball_collision(ball_pos, ball_radius, rods, rod_players, player_radius):
    # Check collision with players
    for rod_index, x in enumerate(rods):
        for patch in rod_players[rod_index]:
            px, py = patch.center
            dist = np.hypot(ball_pos[0] - px, ball_pos[1] - py)
            if dist < ball_radius + player_radius:
                return ('player', rod_index, px, py)
    # Check collision with walls
    if ball_pos[1] - ball_radius <= 0:
        return ('wall', 'top')
    if ball_pos[1] + ball_radius >= table_height:
        return ('wall', 'bottom')
    if ball_pos[0] - ball_radius <= 0:
        return ('wall', 'left')
    if ball_pos[0] + ball_radius >= table_width:
        return ('wall', 'right')
    return None

# Animate
def animate(frame):
    now = time.time()
    for i in range(4):
        dt = now - rod_last_time[i]
        rod_last_time[i] = now
        step = rod_pids[i].update(rod_targets[i], rod_positions[i], dt)
        rod_positions[i] = clamp(rod_positions[i] + step, min_rod_y, max_rod_y)


    # Ball physics simulation
    ball_x, ball_y = ball.center
    vx, vy = drag_data["vx"], drag_data["vy"]
    ball_speed = np.hypot(vx, vy)
    # If random_path is active, move ball along the segment
    if random_path["active"]:
        # ...existing code...
        direction = random_path["direction"]
        speed = random_path["speed"] * BALL_SPEED_FACTOR * 8.0  # Much faster
        friction = 0.98  # Friction factor per frame
        next_pos = np.array([ball_x, ball_y]) + direction * speed
        bounced = False
        # Bounce off walls
        if next_pos[0] - ball.radius <= 0 or next_pos[0] + ball.radius >= table_width:
            direction[0] = -direction[0]
            next_pos[0] = clamp(next_pos[0], ball.radius, table_width - ball.radius)
            bounced = True
        if next_pos[1] - ball.radius <= 0 or next_pos[1] + ball.radius >= table_height:
            direction[1] = -direction[1]
            next_pos[1] = clamp(next_pos[1], ball.radius, table_height - ball.radius)
            bounced = True
        # Check collision with players
        collision = detect_ball_collision(next_pos, ball.radius, rod_x_asymptote_pixels, rod_players, player_radius)
        # Ball trapping logic: if ball speed < 10 and touching player, trap ball; else bounce off
        if collision and collision[0] == 'player':
            if speed < 10:
                px, py = collision[2], collision[3]
                next_pos[0] = px + (next_pos[0] - px)  # Stop at contact point
                next_pos[1] = py + (next_pos[1] - py)
                random_path["active"] = False
                drag_data["vx"] = 0
                drag_data["vy"] = 0
                ball_x, ball_y = next_pos[0], next_pos[1]
                drag_data["x"], drag_data["y"] = ball_x, ball_y
                ball.set_center((ball_x, ball_y))
            else:
                # Bounce off player as normal
                px, py = collision[2], collision[3]
                dx = next_pos[0] - px
                dy = next_pos[1] - py
                dist = np.hypot(dx, dy)
                if dist == 0:
                    dx, dy = 0, -1
                norm = np.hypot(dx, dy)
                if norm == 0:
                    norm = 1
                # Place ball just outside player
                next_pos[0] = px + (dx / norm) * (player_radius + ball.radius + 1)
                next_pos[1] = py + (dy / norm) * (player_radius + ball.radius + 1)
                # Reflect direction and decelerate
                direction = -direction
                random_path["speed"] *= friction * 0.85  # Lose more speed on player bounce
                bounced = True
        elif collision and collision[0] == 'wall':
            # Ball hits wall: bounce (already handled above)
            pass
        random_path["direction"] = direction
        # Decelerate after each bounce or frame
        if bounced:
            random_path["speed"] *= friction * 0.95  # Extra loss on bounce
        else:
            random_path["speed"] *= friction
        # Stop if speed is very low
        if random_path["speed"] < 0.5:
            random_path["active"] = False
            drag_data["vx"] = 0
            drag_data["vy"] = 0
        ball_x, ball_y = next_pos[0], next_pos[1]
        drag_data["x"], drag_data["y"] = ball_x, ball_y
        ball.set_center((ball_x, ball_y))
    else:
        # Normal ball movement
        vx *= BALL_SPEED_FACTOR
        vy *= BALL_SPEED_FACTOR
        ball_x += vx
        ball_y += vy
        collision = detect_ball_collision((ball_x, ball_y), ball.radius, rod_x_asymptote_pixels, rod_players, player_radius)
        # Ball trapping logic: if ball speed < 10 and touching player, do strafe+pass or strafe+shoot
        if collision and collision[0] == 'player':
            if np.hypot(vx, vy) < 10:
                # --- Begin new strafe+pass/shoot state machine ---
                if not hasattr(animate, "foos_state"):
                    animate.foos_state = "idle"
                    animate.foos_timer = 0
                    animate.foos_target_y = None
                    animate.foos_strafe_amt = None
                # Possession: find which rod/player has the ball
                possessor = None
                for rod_index, rod_x in enumerate(rod_x_asymptote_pixels):
                    for patch in rod_players[rod_index]:
                        px, py = patch.center
                        dist = np.hypot(ball_x - px, ball_y - py)
                        if dist < player_radius + ball.radius + 1:
                            possessor = (rod_index, px, py)
                if animate.foos_state == "idle" and possessor is not None:
                    rod_index, px, py = possessor
                    import random
                    n_players = player_counts[rod_index]
                    total_span = table_height - 2 * player_radius
                    spacing = total_span / (n_players + 1)
                    player_centers = [player_radius + (i + 1) * spacing for i in range(n_players)]
                    distances = [abs(ball_y - pc) for pc in player_centers]
                    intercept_idx = np.argmin(distances)
                    if rod_index == 0:
                        # --- FINAL ROW: edge player logic (leave as is for now) ---
                        n_players = 3
                        distances = [abs(ball_y - pc) for pc in player_centers]
                        intercept_idx = np.argmin(distances)
                        # For edge players, allow the rod to move so the player can reach the ball at the very top/bottom
                        offset = ball_y - player_centers[intercept_idx]
                        min_offset = player_radius - player_centers[intercept_idx]
                        max_offset = (table_height - player_radius) - player_centers[intercept_idx]
                        offset = clamp(offset, min_offset, max_offset)
                        # Add a small random strafe for realism
                        if intercept_idx == 1:
                            amt = random.uniform(20, 40)
                            direction = random.choice([-1, 1])
                            target_y = clamp(player_centers[1] + offset + direction * amt, player_radius, table_height - player_radius)
                        elif intercept_idx == 0:
                            target_y = clamp(player_centers[0] + offset, player_radius, table_height - player_radius)
                        elif intercept_idx == 2:
                            target_y = clamp(player_centers[2] + offset, player_radius, table_height - player_radius)
                    else:
                        # --- ALL OTHER RODS: classic pass logic for any player ---
                        amt = random.uniform(10, 30)
                        direction = random.choice([-1, 1])
                        target_y = clamp(player_centers[intercept_idx] + direction * amt, player_radius, table_height - player_radius)
                    animate.foos_target_y = target_y
                    animate.foos_intercept_idx = intercept_idx
                    animate.foos_state = "strafe"
                    animate.foos_timer = now
                    animate.foos_rod = rod_index
                    animate.foos_is_final = (rod_index == 0)
                    animate.foos_launch_delay = random.uniform(0.15, 0.35)
                elif animate.foos_state == "strafe":
                    # Smoothly move rod and ball together to target_y using player-centering logic (for ALL rods)
                    rod_index = animate.foos_rod
                    target_y = animate.foos_target_y
                    intercept_idx = animate.foos_intercept_idx
                    n_players = player_counts[rod_index]
                    total_span = table_height - 2 * player_radius
                    spacing = total_span / (n_players + 1)
                    player_centers = [player_radius + (i + 1) * spacing for i in range(n_players)]
                    offset = target_y - player_centers[intercept_idx]
                    min_offset = player_radius - min(player_centers)
                    max_offset = (table_height - player_radius) - max(player_centers)
                    offset = clamp(offset, min_offset, max_offset)
                    current_positions = [patch.center[1] for patch in rod_players[rod_index]]
                    target_positions = [pc + offset for pc in player_centers]
                    move_speed = 0.12
                    new_positions = [cur + move_speed * (tgt - cur) for cur, tgt in zip(current_positions, target_positions)]
                    for i, patch in enumerate(rod_players[rod_index]):
                        patch.center = (rod_x_asymptote_pixels[rod_index], new_positions[i])
                    # Ball is locked to the intercepting player
                    ball_y_locked = new_positions[intercept_idx]
                    ball_x_locked = rod_x_asymptote_pixels[rod_index]
                    ball.set_center((ball_x_locked, ball_y_locked))
                    drag_data["x"] = ball_x_locked
                    drag_data["y"] = ball_y_locked
                    # Wait a short, random time, then pass or shoot strictly horizontally
                    if abs(ball_y_locked - target_y) < 1.5 and now - animate.foos_timer > animate.foos_launch_delay:
                        launch_x = ball_x_locked + player_radius + ball.radius + 1
                        launch_y = ball_y_locked
                        if animate.foos_is_final:
                            # For last row, shoot after a short randomized delay for any player
                            # (no y-range check, just use the same delay logic as passes)
                            start = np.array([launch_x, launch_y])
                            end = np.array([table_width, launch_y])
                            direction = np.array([1.0, 0.0])
                            shot_speed = 4.0
                            random_path["active"] = True
                            random_path["start"] = start
                            random_path["end"] = end
                            random_path["speed"] = shot_speed
                            random_path["direction"] = direction
                            random_path["t"] = 0
                            random_path["length"] = np.linalg.norm(end - start)
                            drag_data["vx"] = 0
                            drag_data["vy"] = 0
                            ball.set_center((launch_x, launch_y))
                            print(f"SHOT! Rod {rod_index}, y={launch_y:.1f}")
                            animate.foos_state = "idle"
                        else:
                            # Restore original pass logic for rods 1,2,3
                            next_rod_index = rod_index + 1
                            if next_rod_index < len(rod_x_asymptote_pixels):
                                end_x = rod_x_asymptote_pixels[next_rod_index]
                            else:
                                end_x = table_width
                            start = np.array([launch_x, launch_y])
                            end = np.array([end_x, launch_y])
                            direction = np.array([1.0, 0.0])
                            pass_speed = 1.0
                            random_path["active"] = True
                            random_path["start"] = start
                            random_path["end"] = end
                            random_path["speed"] = pass_speed
                            random_path["direction"] = direction
                            random_path["t"] = 0
                            random_path["length"] = np.linalg.norm(end - start)
                            drag_data["vx"] = 0
                            drag_data["vy"] = 0
                            ball.set_center((launch_x, launch_y))
                            print(f"Pass: Rod {rod_index} to {next_rod_index}, y={launch_y:.1f}")
                            animate.foos_state = "idle"
                elif animate.foos_state == "front_strafe":
                    # Move rod and ball together to random y=200..300 (intertwined)
                    rod_index = animate.foos_rod
                    target_y = animate.foos_target_y
                    n_players = player_counts[rod_index]
                    total_span = table_height - 2 * player_radius
                    spacing = total_span / (n_players + 1)
                    player_centers = [player_radius + (i + 1) * spacing for i in range(n_players)]
                    distances = [abs(target_y - pc) for pc in player_centers]
                    intercept_idx = np.argmin(distances)
                    offset = target_y - player_centers[intercept_idx]
                    min_offset = player_radius - min(player_centers)
                    max_offset = (table_height - player_radius) - max(player_centers)
                    offset = clamp(offset, min_offset, max_offset)
                    new_positions = [pc + offset for pc in player_centers]
                    for i, patch in enumerate(rod_players[rod_index]):
                        patch.center = (rod_x_asymptote_pixels[rod_index], new_positions[i])
                    # Ball is locked to the rod during strafe
                    ball.set_center((rod_x_asymptote_pixels[rod_index], target_y))
                    drag_data["x"] = rod_x_asymptote_pixels[rod_index]
                    drag_data["y"] = target_y
                    # Wait a short time, then shoot hard using teleport-style trajectory
                    if now - animate.foos_timer > 0.18:
                        # Shoot hard in positive x direction
                        start = np.array([rod_x_asymptote_pixels[rod_index], target_y])
                        end = np.array([table_width, target_y])
                        direction = end - start
                        norm = np.linalg.norm(direction)
                        if norm == 0:
                            direction = np.array([1, 0])
                            norm = 1
                        direction = direction / norm
                        shot_speed = 7.33  # 1/3 of previous (was 22)
                        random_path["active"] = True
                        random_path["start"] = start
                        random_path["end"] = end
                        random_path["speed"] = shot_speed
                        random_path["direction"] = direction
                        random_path["t"] = 0
                        random_path["length"] = np.linalg.norm(end - start)
                        drag_data["vx"] = 0
                        drag_data["vy"] = 0
                        print(f"SHOT! Rod {rod_index}, y={target_y:.1f}")
                        animate.foos_state = "idle"
                        animate.foos_ball_locked = False
                return
            else:
                # Bounce off player as normal
                px, py = collision[2], collision[3]
                dx = ball_x - px
                dy = ball_y - py
                dist = np.hypot(dx, dy)
                if dist == 0:
                    dx, dy = 0, -1
                norm = np.hypot(dx, dy)
                if norm == 0:
                    norm = 1
                ball_x = px + (dx / norm) * (player_radius + ball.radius + 1)
                ball_y = py + (dy / norm) * (player_radius + ball.radius + 1)
                vx, vy = 0, 0
        elif collision and collision[0] == 'wall':
            # Ball hits wall: bounce
            if collision[1] == 'top' or collision[1] == 'bottom':
                vy = -vy * BALL_BOUNCE_FACTOR
            if collision[1] == 'left' or collision[1] == 'right':
                vx = -vx * BALL_BOUNCE_FACTOR
            ball_x = clamp(ball_x, ball.radius, table_width - ball.radius)
            ball_y = clamp(ball_y, ball.radius, table_height - ball.radius)
        ball.set_center((ball_x, ball_y))
        drag_data["vx"], drag_data["vy"] = vx, vy
        drag_data["x"], drag_data["y"] = ball_x, ball_y

    update_player_positions()

    targets_disp = ", ".join(f"{rod_targets[i]:.2f}" for i in range(4))
    positions_disp = ", ".join(f"{rod_positions[i]:.2f}" for i in range(4))
    state_text.set_text(
        f"Rods P: [{positions_disp}]\nRods T: [{targets_disp}]"
    )

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('motion_notify_event', on_motion)

def on_double_click(event):
    global random_path
    if event.dblclick:
        # Teleport ball to cursor and launch along a random path
        ball.set_center((event.xdata, event.ydata))
        drag_data["x"] = event.xdata
        drag_data["y"] = event.ydata
        import random
        angle = random.uniform(0, 2 * np.pi)
        length = random.uniform(100, 400)  # Path length in pixels
        speed = random.uniform(3, 10)      # Ball speed in pixels/frame
        ball_x, ball_y = event.xdata, event.ydata
        end_x = ball_x + np.cos(angle) * length
        end_y = ball_y + np.sin(angle) * length
        # Clamp end point to table bounds
        end_x = clamp(end_x, ball.radius, table_width - ball.radius)
        end_y = clamp(end_y, ball.radius, table_height - ball.radius)
        direction = np.array([end_x - ball_x, end_y - ball_y])
        norm = np.linalg.norm(direction)
        if norm == 0:
            direction = np.array([1, 0])
            norm = 1
        direction = direction / norm
        path_vec = np.array([end_x - ball_x, end_y - ball_y])
        path_length = np.linalg.norm(path_vec)
        random_path["active"] = True
        random_path["start"] = np.array([ball_x, ball_y])
        random_path["end"] = np.array([end_x, end_y])
        random_path["speed"] = speed
        random_path["direction"] = direction
        random_path["t"] = 0
        random_path["length"] = path_length
        drag_data["vx"] = 0
        drag_data["vy"] = 0
        ball_windup["active"] = False
        print(f"Ball teleported to ({event.xdata}, {event.ydata}) and launched along path to ({end_x:.1f},{end_y:.1f}) at speed {speed:.2f}")

fig.canvas.mpl_connect('button_press_event', on_double_click)

ani = FuncAnimation(fig, animate, interval=20)
plt.show()

## REMOVE DUPLICATE random_path DEFINITION

def on_key_press(event):
    global random_path
    if event.key == ' ':  # Space bar
        import random
        # Pick a random direction and length
        angle = random.uniform(0, 2 * np.pi)
        length = random.uniform(100, 400)  # Path length in pixels
        speed = random.uniform(3, 10)      # Ball speed in pixels/frame
        ball_x, ball_y = ball.center
        end_x = ball_x + np.cos(angle) * length
        end_y = ball_y + np.sin(angle) * length
        # Clamp end point to table bounds
        end_x = clamp(end_x, ball.radius, table_width - ball.radius)
        end_y = clamp(end_y, ball.radius, table_height - ball.radius)
        direction = np.array([end_x - ball_x, end_y - ball_y])
        norm = np.linalg.norm(direction)
        if norm == 0:
            direction = np.array([1, 0])
            norm = 1
        direction = direction / norm
        path_vec = np.array([end_x - ball_x, end_y - ball_y])
        path_length = np.linalg.norm(path_vec)
        random_path["active"] = True
        random_path["start"] = np.array([ball_x, ball_y])
        random_path["end"] = np.array([end_x, end_y])
        random_path["speed"] = speed
        random_path["direction"] = direction
        random_path["t"] = 0
        random_path["length"] = path_length
        drag_data["vx"] = 0
        drag_data["vy"] = 0
        print(f"Space bar: Ball path from ({ball_x:.1f},{ball_y:.1f}) to ({end_x:.1f},{end_y:.1f}) at speed {speed:.2f}")

fig.canvas.mpl_connect('key_press_event', on_key_press)

# --- Patch animate to follow random path ---
old_animate = animate

def animate(frame):
    now = time.time()
    for i in range(4):
        dt = now - rod_last_time[i]
        rod_last_time[i] = now
        step = rod_pids[i].update(rod_targets[i], rod_positions[i], dt)
        rod_positions[i] = clamp(rod_positions[i] + step, min_rod_y, max_rod_y)

    # Ball physics simulation
    ball_x, ball_y = ball.center
    vx, vy = drag_data["vx"], drag_data["vy"]
    # If random_path is active, move ball along the segment
    if random_path["active"]:
        # Move ball along the line segment using parameter t
        speed = random_path["speed"] * BALL_SPEED_FACTOR
        t = random_path["t"]
        length = random_path["length"]
        if length == 0:
            # Degenerate case, just set to end
            pos = random_path["end"]
            random_path["active"] = False
        else:
            t_new = t + speed
            if t_new >= length:
                t_new = length
                random_path["active"] = False
            pos = random_path["start"] + (random_path["end"] - random_path["start"]) * (t_new / length)
            random_path["t"] = t_new
        ball_x, ball_y = pos[0], pos[1]
        drag_data["x"], drag_data["y"] = ball_x, ball_y
        ball.set_center((ball_x, ball_y))
        drag_data["vx"] = 0
        drag_data["vy"] = 0
    else:
        # Normal ball movement
        vx *= BALL_SPEED_FACTOR
        vy *= BALL_SPEED_FACTOR
        ball_x += vx
        ball_y += vy
        collision = detect_ball_collision((ball_x, ball_y), ball.radius, rod_x_asymptote_pixels, rod_players, player_radius)
        if collision:
            if collision[0] == 'player':
                # Ball hits player: stop in front of them, not under
                px, py = collision[2], collision[3]
                dx = ball_x - px
                dy = ball_y - py
                dist = np.hypot(dx, dy)
                if dist == 0:
                    dx, dy = 0, -1
                norm = np.hypot(dx, dy)
                if norm == 0:
                    norm = 1
                ball_x = px + (dx / norm) * (player_radius + ball.radius + 1)
                ball_y = py + (dy / norm) * (player_radius + ball.radius + 1)
                vx, vy = 0, 0
            elif collision[0] == 'wall':
                # Ball hits wall: bounce
                if collision[1] == 'top' or collision[1] == 'bottom':
                    vy = -vy * BALL_BOUNCE_FACTOR
                if collision[1] == 'left' or collision[1] == 'right':
                    vx = -vx * BALL_BOUNCE_FACTOR
                ball_x = clamp(ball_x, ball.radius, table_width - ball.radius)
                ball_y = clamp(ball_y, ball.radius, table_height - ball.radius)
    ball.set_center((ball_x, ball_y))
    drag_data["vx"], drag_data["vy"] = vx, vy
    drag_data["x"], drag_data["y"] = ball_x, ball_y

    update_player_positions()

    targets_disp = ", ".join(f"{rod_targets[i]:.2f}" for i in range(4))
    positions_disp = ", ".join(f"{rod_positions[i]:.2f}" for i in range(4))
    state_text.set_text(
        f"Rods P: [{positions_disp}]\nRods T: [{targets_disp}]"
    )