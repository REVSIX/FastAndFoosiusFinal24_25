import time

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, Rectangle

# Constants for table and rods
TABLE_WIDTH, TABLE_HEIGHT = 800, 480
ROD_X = [401, 254, 105, 29]
PLAYER_AREAS = [
    [(19, 112), (112, 206), (206, 297)],
    [(17, 68), (80, 131), (142, 192), (202, 251), (264, 313)],
    [(18, 185), (146, 311)],
    [(23, 127), (117, 220), (211, 314)]
]

# Ball and rod state (updated externally)
ball_pos = [TABLE_WIDTH//2, TABLE_HEIGHT//2]
motor_pos = [0.5]*4
motor_target = [0.5]*4
servo_pos = [0]*4
servo_target = [0]*4

# State storage for error plot
error_history = []  # List of (time, motor_err0-3, servo_err0-3)

# Determine mode from flags passed by main file
MODE = "FULL_SIM"  # Options: "FULL_SIM", "CAM_ONLY", "FULL_REAL"

# Setup Figure
fig, (ax_field, ax_err) = plt.subplots(1, 2, figsize=(12, 6))
fig.canvas.manager.set_window_title("FoosScope: Foosball Visualizer")

# --- FIELD DISPLAY SETUP ---
ax_field.set_xlim(0, TABLE_WIDTH)
ax_field.set_ylim(0, TABLE_HEIGHT)
ax_field.set_aspect('equal')
ax_field.set_facecolor('forestgreen')
ax_field.invert_yaxis()
ax_field.set_title("Foosball Table")

# Draw table and rods
ax_field.add_patch(Rectangle((0, 0), TABLE_WIDTH, TABLE_HEIGHT, edgecolor='white', lw=3, facecolor='none'))
rod_lines = [ax_field.plot([x, x], [0, TABLE_HEIGHT], color='white', lw=2)[0] for x in ROD_X]

# Draw ball
ball_artist = Circle((ball_pos[0], ball_pos[1]), radius=10, color='white')
ax_field.add_patch(ball_artist)

# Draw player zones
player_patches = []
for i, x in enumerate(ROD_X):
    patches = []
    for (start, end) in PLAYER_AREAS[i]:
        rect = Rectangle((x - 15, start), 30, end - start, edgecolor='yellow', facecolor='black')
        ax_field.add_patch(rect)
        patches.append(rect)
    player_patches.append(patches)

# --- ERROR PLOT SETUP ---
ax_err.set_title("Stepper + Servo Error Over Time")
ax_err.set_xlim(0, 10)  # Show last 10 seconds
ax_err.set_ylim(-1, 1)
ax_err.set_xlabel("Time (s)")
ax_err.set_ylabel("Error")
err_lines_motor = [ax_err.plot([], [], label=f"M{i}")[0] for i in range(4)]
err_lines_servo = [ax_err.plot([], [], label=f"S{i}", linestyle='--')[0] for i in range(4)]
ax_err.legend()

# --- UPDATE FUNCTION ---
def update(frame):
    now = time.time()
    # Update ball
    ball_artist.set_center((ball_pos[0], ball_pos[1]))

    # Update error history
    errors = [motor_target[i]-motor_pos[i] for i in range(4)] + [servo_target[i]-servo_pos[i] for i in range(4)]
    error_history.append((now, *errors))
    error_history[:] = [entry for entry in error_history if now - entry[0] <= 10]  # Keep 10s

    times = [entry[0] - error_history[0][0] for entry in error_history]
    for i in range(4):
        err_lines_motor[i].set_data(times, [entry[1+i] for entry in error_history])
        err_lines_servo[i].set_data(times, [entry[5+i] for entry in error_history])
    ax_err.set_xlim(max(0, times[0]), times[-1]+0.1)

    return [ball_artist] + err_lines_motor + err_lines_servo

ani = FuncAnimation(fig, update, interval=30, blit=True)

plt.tight_layout()
plt.show()
