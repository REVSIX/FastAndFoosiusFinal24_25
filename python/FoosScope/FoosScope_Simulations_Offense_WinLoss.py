import numpy as np
import matplotlib.pyplot as plt
import random

# --- Constants ---
TABLE_WIDTH, TABLE_HEIGHT = 800, 480
ROD_XS = [595, 373, 147, 36]
PLAYER_COUNTS = [3, 5, 2, 3]
PLAYER_RADIUS = 16
BALL_RADIUS = 10
GOAL_Y_MIN, GOAL_Y_MAX = 175, 325
GOAL_LEFT_X = 25
GOAL_RIGHT_X = 775
BALL_FRICTION = 0.98
BOUNCE_FACTOR = 0.7
PASS_SPEED = 4.0
SHOT_SPEED = 6.5
ROD_MAX_SPEED = 18  # pixels per step

# --- Helper Functions ---
def clamp(val, min_val, max_val):
    return max(min(val, max_val), min_val)

def get_player_centers(center_y, n):
    spacing = (TABLE_HEIGHT - 2 * PLAYER_RADIUS) / (n + 1)
    center_idx = n // 2
    return [clamp(center_y + (i - center_idx) * spacing, PLAYER_RADIUS, TABLE_HEIGHT - PLAYER_RADIUS) for i in range(n)]

def predict_cross_y(ball_x, ball_y, vx, vy, rod_x):
    if vx == 0:
        return ball_y
    t = (rod_x - ball_x) / vx
    return clamp(ball_y + vy * t, PLAYER_RADIUS, TABLE_HEIGHT - PLAYER_RADIUS)

def detect_collision(ball_x, ball_y, rod_x, player_ys):
    for py in player_ys:
        if np.hypot(ball_x - rod_x, ball_y - py) < PLAYER_RADIUS + BALL_RADIUS:
            return py
    return None

# --- Main Simulation Function ---
def simulate_one_play():
    # Ball starts behind last offensive rod, random y
    ball_x = random.uniform(ROD_XS[0] - 80, ROD_XS[0] - 30)
    ball_y = random.uniform(PLAYER_RADIUS, TABLE_HEIGHT - PLAYER_RADIUS)
    vx, vy = PASS_SPEED, 0
    rod_centers = [TABLE_HEIGHT / 2 for _ in ROD_XS]
    # Pass through rods 1,2,3 (right to left), targeting random players
    for rod_idx in range(1, len(ROD_XS)):
        next_rod_x = ROD_XS[rod_idx]
        n_players = PLAYER_COUNTS[rod_idx]
        # Choose a random player to pass to
        player_centers = get_player_centers(TABLE_HEIGHT/2, n_players)
        target_player = random.randint(0, n_players-1)
        # Add some random offset to make it less deterministic
        amt = random.uniform(-10, 10)
        target_y = clamp(player_centers[target_player] + amt, PLAYER_RADIUS, TABLE_HEIGHT - PLAYER_RADIUS)
        # Move rod center toward target_y with speed limit
        dy = target_y - rod_centers[rod_idx]
        move = np.clip(dy, -ROD_MAX_SPEED, ROD_MAX_SPEED)
        rod_centers[rod_idx] = clamp(rod_centers[rod_idx] + move, PLAYER_RADIUS, TABLE_HEIGHT - PLAYER_RADIUS)
        player_ys = get_player_centers(rod_centers[rod_idx], n_players)
        # Stepwise pass
        steps = int(abs(next_rod_x - ball_x) // 8) + 1
        for step in range(steps):
            frac = (step + 1) / steps
            interp_x = ball_x + (next_rod_x - ball_x) * frac
            interp_y = ball_y + (target_y - ball_y) * frac
            # Check collision
            hit = detect_collision(interp_x, interp_y, next_rod_x, player_ys)
            if hit is not None:
                ball_x, ball_y = next_rod_x, hit
                break
            if step == steps - 1:
                ball_x, ball_y = next_rod_x, target_y
    # Final rod: strafe, then shoot horizontally (VirtualFoosScope style)
    rod_idx = 0
    n_players = PLAYER_COUNTS[0]
    # Choose a random player to strafe to
    player_centers = get_player_centers(TABLE_HEIGHT/2, n_players)
    target_player = random.randint(0, n_players-1)
    amt = random.uniform(-10, 10)
    target_y = clamp(player_centers[target_player] + amt, PLAYER_RADIUS, TABLE_HEIGHT - PLAYER_RADIUS)
    # Move rod center toward target_y
    dy = target_y - rod_centers[0]
    move = np.clip(dy, -ROD_MAX_SPEED, ROD_MAX_SPEED)
    rod_centers[0] = clamp(rod_centers[0] + move, PLAYER_RADIUS, TABLE_HEIGHT - PLAYER_RADIUS)
    player_ys = get_player_centers(rod_centers[0], n_players)
    # Strafe offset logic
    distances = [abs(ball_y - py) for py in player_ys]
    intercept_idx = np.argmin(distances)
    offset = ball_y - player_ys[intercept_idx]
    min_offset = PLAYER_RADIUS - player_ys[intercept_idx]
    max_offset = (TABLE_HEIGHT - PLAYER_RADIUS) - player_ys[intercept_idx]
    offset = clamp(offset, min_offset, max_offset)
    # Strafe to new y
    ball_y = clamp(player_ys[intercept_idx] + offset, PLAYER_RADIUS, TABLE_HEIGHT - PLAYER_RADIUS)
    # Shoot at a random angle (not just horizontal)
    launch_x = ROD_XS[0] + PLAYER_RADIUS + BALL_RADIUS + 1
    launch_y = ball_y
    angle = random.uniform(-0.35, 0.35)  # ~±20 degrees
    vx = SHOT_SPEED * np.cos(angle)
    vy = SHOT_SPEED * np.sin(angle)
    ball_x = launch_x
    ball_y = launch_y
    # Defense rods (mirror positions)
    DEF_ROD_XS = [TABLE_WIDTH - x for x in ROD_XS]
    DEF_PLAYER_COUNTS = PLAYER_COUNTS
    DEF_BLOCK_RADIUS = PLAYER_RADIUS
    DEF_MAX_SPEED = 7  # More realistic defense speed
    DEF_ERROR = 24     # Larger error for more realism
    def_rod_centers = [TABLE_HEIGHT / 2 for _ in DEF_ROD_XS]
    goalie_delay = 0
    GOALIE_DELAY_STEPS = 16  # Increased goalie delay
    # Simulate shot stepwise
    while True:
        ball_x += vx * 8  # Larger step for speed
        ball_y += vy * 8
        vx *= BALL_FRICTION
        vy *= BALL_FRICTION
        # Bounce off top/bottom
        if ball_y <= BALL_RADIUS:
            ball_y = BALL_RADIUS
            vy = -vy * BOUNCE_FACTOR
        elif ball_y >= TABLE_HEIGHT - BALL_RADIUS:
            ball_y = TABLE_HEIGHT - BALL_RADIUS
            vy = -vy * BOUNCE_FACTOR
        ball_x = clamp(ball_x, BALL_RADIUS, TABLE_WIDTH - BALL_RADIUS)
        # Move each defense rod center toward ball_y, but add delay for goalie (rod 0)
        for rod_idx in range(len(def_rod_centers)):
            if rod_idx == 0:
                # Goalie delay: only start tracking after a few steps
                if goalie_delay < GOALIE_DELAY_STEPS:
                    goalie_delay += 1
                    continue
            # Add larger random error to defense y-targeting
            error = random.uniform(-DEF_ERROR, DEF_ERROR)
            target_y = clamp(ball_y + error, PLAYER_RADIUS, TABLE_HEIGHT - PLAYER_RADIUS)
            dy = target_y - def_rod_centers[rod_idx]
            move = np.clip(dy, -DEF_MAX_SPEED, DEF_MAX_SPEED)
            def_rod_centers[rod_idx] = clamp(def_rod_centers[rod_idx] + move, PLAYER_RADIUS, TABLE_HEIGHT - PLAYER_RADIUS)
        # Place defense players
        defense_players = []
        for rod_idx, def_x in enumerate(DEF_ROD_XS):
            n_players = DEF_PLAYER_COUNTS[rod_idx]
            player_ys = get_player_centers(def_rod_centers[rod_idx], n_players)
            defense_players.extend([(def_x, py) for py in player_ys])
        # Check for collision with defense
        for def_x, def_y in defense_players:
            if abs(ball_x - def_x) < DEF_BLOCK_RADIUS + BALL_RADIUS and abs(ball_y - def_y) < DEF_BLOCK_RADIUS + BALL_RADIUS:
                dist = np.hypot(ball_x - def_x, ball_y - def_y)
                if dist < DEF_BLOCK_RADIUS + BALL_RADIUS:
                    return ("blocked", launch_x, launch_y, ball_x, ball_y)
        # Check for goal
        if ball_x >= GOAL_RIGHT_X and GOAL_Y_MIN <= ball_y <= GOAL_Y_MAX:
            return ("goal", launch_x, launch_y, ball_x, ball_y)
        if ball_x >= TABLE_WIDTH:
            return ("blocked", launch_x, launch_y, ball_x, ball_y)
        # Early exit if ball is nearly stopped
        if abs(vx) + abs(vy) < 0.2:
            return ("blocked", launch_x, launch_y, ball_x, ball_y)

# --- Batch Simulation and Plotting ---
def run_simulation(num_shots=10000):
    results = {"goal": 0, "blocked": 0}
    start_positions = []
    end_positions = []
    for _ in range(num_shots):
        outcome, sx, sy, ex, ey = simulate_one_play()
        results[outcome] += 1
        start_positions.append([sx, sy])
        end_positions.append([ex, ey])
    start_positions = np.array(start_positions)
    end_positions = np.array(end_positions)
    # Plot heatmap
    plt.figure(figsize=(10, 6))
    plt.hexbin(start_positions[:,0], start_positions[:,1], gridsize=50, cmap='Blues', alpha=0.5, mincnt=1, label='Start')
    plt.hexbin(end_positions[:,0], end_positions[:,1], gridsize=50, cmap='Reds', alpha=0.5, mincnt=1, label='End')
    plt.xlim(0, TABLE_WIDTH)
    plt.ylim(0, TABLE_HEIGHT)
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.title('Offense First Play (Physics, Defense Sim Style) Start (Blue) and End (Red) Heatmap')
    # Annotate stats
    total = results["goal"] + results["blocked"]
    goal_pct = 100.0 * results["goal"] / total
    block_pct = 100.0 * results["blocked"] / total
    stats_text = f"Goals: {results['goal']} ({goal_pct:.2f}%)\nBlocked: {results['blocked']} ({block_pct:.2f}%)"
    plt.text(10, TABLE_HEIGHT-30, stats_text, fontsize=12, color='black', va='top', ha='left', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    filename = f"winloss_chart_firstplay.png"
    plt.savefig(filename)
    print(f'Heatmap saved as {filename}')
    print(stats_text)
    plt.show()

if __name__ == "__main__":
    run_simulation(10000)
