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
    # Kick and go: Ball starts behind last offensive rod, random y, and is shot hard and straight (no passing, no strafe, no directional control)
    launch_x = ROD_XS[0] + PLAYER_RADIUS + BALL_RADIUS + 1
    launch_y = random.uniform(PLAYER_RADIUS, TABLE_HEIGHT - PLAYER_RADIUS)
    vx = SHOT_SPEED * 2.5  # Match WinLoss sim speed
    vy = 0
    ball_x = launch_x
    ball_y = launch_y
    # Defense rods (mirror positions)
    DEF_ROD_XS = [TABLE_WIDTH - x for x in ROD_XS]
    DEF_PLAYER_COUNTS = PLAYER_COUNTS
    DEF_BLOCK_RADIUS = PLAYER_RADIUS
    DEF_MAX_SPEED = 7  # More realistic defense speed
    DEF_ERROR = 40     # Even larger error for more realism
    def_rod_centers = [TABLE_HEIGHT / 2 for _ in DEF_ROD_XS]
    goalie_delay = 0
    GOALIE_DELAY_STEPS = 32  # Much longer goalie delay
    # Simulate shot stepwise
    while True:
        prev_x, prev_y = ball_x, ball_y
        ball_x += vx * 16
        ball_y += vy * 16
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
        # Predictive defense: for each rod, predict where ball will cross its x and move rod center toward that y
        for rod_idx in range(len(def_rod_centers)):
            def_x = DEF_ROD_XS[rod_idx]
            if rod_idx == 0:
                # Goalie delay: only start tracking after a few steps
                if goalie_delay < GOALIE_DELAY_STEPS:
                    goalie_delay += 1
                    continue
            # Predict crossing
            if vx != 0:
                t_cross = (def_x - prev_x) / (ball_x - prev_x) if (ball_x - prev_x) != 0 else 0
                cross_y = prev_y + (ball_y - prev_y) * t_cross if 0 <= t_cross <= 1 else ball_y
            else:
                cross_y = ball_y
            error = random.uniform(-DEF_ERROR, DEF_ERROR)
            target_y = clamp(cross_y + error, PLAYER_RADIUS, TABLE_HEIGHT - PLAYER_RADIUS)
            dy = target_y - def_rod_centers[rod_idx]
            move = np.clip(dy, -DEF_MAX_SPEED * 1.5, DEF_MAX_SPEED * 1.5)
            def_rod_centers[rod_idx] = clamp(def_rod_centers[rod_idx] + move, PLAYER_RADIUS, TABLE_HEIGHT - PLAYER_RADIUS)
        # Place defense players
        defense_players = []
        for rod_idx, def_x in enumerate(DEF_ROD_XS):
            n_players = DEF_PLAYER_COUNTS[rod_idx]
            player_ys = get_player_centers(def_rod_centers[rod_idx], n_players)
            defense_players.extend([(def_x, py) for py in player_ys])
        # Check for collision at crossing point
        for def_x, def_y in defense_players:
            # Check if ball crossed this rod between prev_x and ball_x
            crossed = (prev_x - def_x) * (ball_x - def_x) <= 0
            if crossed:
                # Interpolate y at crossing
                if ball_x != prev_x:
                    t_cross = (def_x - prev_x) / (ball_x - prev_x)
                    cross_y = prev_y + (ball_y - prev_y) * t_cross
                else:
                    cross_y = ball_y
                if abs(cross_y - def_y) < DEF_BLOCK_RADIUS + BALL_RADIUS:
                    dist = np.hypot(def_x - def_x, cross_y - def_y)
                    if dist < DEF_BLOCK_RADIUS + BALL_RADIUS:
                        return ("blocked", launch_x, launch_y, def_x, cross_y)
        # Check for goal
        if ball_x >= GOAL_RIGHT_X and GOAL_Y_MIN <= ball_y <= GOAL_Y_MAX:
            return ("goal", launch_x, launch_y, ball_x, ball_y)
        if ball_x >= TABLE_WIDTH:
            return ("blocked", launch_x, launch_y, ball_x, ball_y)
        if abs(vx) + abs(vy) < 0.2:
            return ("blocked", launch_x, launch_y, ball_x, ball_y)

# --- Batch Simulation and Plotting ---
def run_simulation(num_shots=10000):
    results = {"goal": 0, "blocked": 0}
    start_positions = []
    end_positions = []
    outcomes = []
    trajectories = []
    for i in range(num_shots):
        # For trajectory plotting, record the full path for a sample
        # (for efficiency, only record for first 500 shots)
        traj = []
        def record_traj(*args):
            traj.append(args)
        outcome, sx, sy, ex, ey = simulate_one_play()
        results[outcome] += 1
        start_positions.append([sx, sy])
        end_positions.append([ex, ey])
        outcomes.append(outcome)
        if len(trajectories) < 500:
            # Only store start and end for now, but could be extended for full path
            trajectories.append(((sx, sy), (ex, ey), outcome))
        if (i+1) % 1000 == 0:
            print(f"Completed {i+1} trials...")
    start_positions = np.array(start_positions)
    end_positions = np.array(end_positions)
    outcomes = np.array(outcomes)
    # --- 1. Outcome Distribution ---
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    # Bar chart of outcomes
    ax_bar = axes[0,0]
    ax_bar.bar(['Goal', 'Blocked'], [results['goal'], results['blocked']], color=['tab:green', 'tab:red'])
    ax_bar.set_ylabel('Count')
    ax_bar.set_title('Outcome Distribution')
    for i, v in enumerate([results['goal'], results['blocked']]):
        ax_bar.text(i, v + num_shots*0.01, str(v), ha='center', va='bottom', fontsize=12)
    # --- 2. End Position Heatmap (Goals Only) ---
    ax_goalmap = axes[0,1]
    goal_ends = end_positions[outcomes == 'goal']
    if len(goal_ends) > 0:
        hb_goal = ax_goalmap.hexbin(goal_ends[:,0], goal_ends[:,1], gridsize=60, cmap='viridis', alpha=0.9, mincnt=1)
        cb_goal = fig.colorbar(hb_goal, ax=ax_goalmap, orientation='vertical', fraction=0.045, pad=0.02)
        cb_goal.set_label('Goal Density')
    ax_goalmap.set_xlim(0, TABLE_WIDTH)
    ax_goalmap.set_ylim(0, TABLE_HEIGHT)
    ax_goalmap.set_xlabel('X Position')
    ax_goalmap.set_ylabel('Y Position')
    ax_goalmap.set_title('End Positions of Goals')
    # Overlay goal area
    ax_goalmap.axvline(GOAL_RIGHT_X, color='green', linestyle='--', lw=2, alpha=0.7)
    ax_goalmap.fill_betweenx([GOAL_Y_MIN, GOAL_Y_MAX], GOAL_RIGHT_X, TABLE_WIDTH, color='green', alpha=0.1)
    # --- 3. Sample Shot Trajectories ---
    ax_traj = axes[1,0]
    for (sx, sy), (ex, ey), outcome in trajectories:
        color = 'tab:green' if outcome == 'goal' else 'tab:red'
        ax_traj.plot([sx, ex], [sy, ey], color=color, alpha=0.15 if outcome == 'blocked' else 0.3, lw=1)
    ax_traj.set_xlim(0, TABLE_WIDTH)
    ax_traj.set_ylim(0, TABLE_HEIGHT)
    ax_traj.set_xlabel('X Position')
    ax_traj.set_ylabel('Y Position')
    ax_traj.set_title('Sample Shot Trajectories')
    # Overlay goal area
    ax_traj.axvline(GOAL_RIGHT_X, color='green', linestyle='--', lw=2, alpha=0.7)
    ax_traj.fill_betweenx([GOAL_Y_MIN, GOAL_Y_MAX], GOAL_RIGHT_X, TABLE_WIDTH, color='green', alpha=0.1)
    # --- 4. Efficiency Map (Goal Rate by Launch Position) ---
    ax_eff = axes[1,1]
    # Bin start positions and compute goal rate per bin
    bins_x = np.linspace(0, TABLE_WIDTH, 40)
    bins_y = np.linspace(0, TABLE_HEIGHT, 24)
    goal_mask = (outcomes == 'goal')
    hist_all, _, _ = np.histogram2d(start_positions[:,0], start_positions[:,1], bins=[bins_x, bins_y])
    hist_goal, _, _ = np.histogram2d(start_positions[goal_mask,0], start_positions[goal_mask,1], bins=[bins_x, bins_y])
    with np.errstate(divide='ignore', invalid='ignore'):
        eff_map = np.nan_to_num(hist_goal / hist_all)
    im = ax_eff.imshow(eff_map.T, origin='lower', extent=[0, TABLE_WIDTH, 0, TABLE_HEIGHT], aspect='auto', cmap='YlGnBu', vmin=0, vmax=1)
    cb_eff = fig.colorbar(im, ax=ax_eff, orientation='vertical', fraction=0.045, pad=0.02)
    cb_eff.set_label('Goal Rate')
    ax_eff.set_xlabel('X Position')
    ax_eff.set_ylabel('Y Position')
    ax_eff.set_title('Efficiency Map (Goal Rate by Launch Position)')
    # Overlay goal area
    ax_eff.axvline(GOAL_RIGHT_X, color='green', linestyle='--', lw=2, alpha=0.7)
    ax_eff.fill_betweenx([GOAL_Y_MIN, GOAL_Y_MAX], GOAL_RIGHT_X, TABLE_WIDTH, color='green', alpha=0.1)
    # --- 5. Statistical Summary ---
    total = results["goal"] + results["blocked"]
    goal_pct = 100.0 * results["goal"] / total
    block_pct = 100.0 * results["blocked"] / total
    mean_shot_dist = np.mean(np.linalg.norm(end_positions - start_positions, axis=1))
    std_shot_dist = np.std(np.linalg.norm(end_positions - start_positions, axis=1))
    stats_text = (
        f"Goals: {results['goal']} ({goal_pct:.2f}%)\n"
        f"Blocked: {results['blocked']} ({block_pct:.2f}%)\n"
        f"Mean Shot Distance: {mean_shot_dist:.1f} px\n"
        f"Std Shot Distance: {std_shot_dist:.1f} px\n"
        f"Total Shots: {total}"
    )
    fig.suptitle('Offense Efficiency Analysis (Physics, Defense Sim Style)', fontsize=18)
    # Place summary on empty space in bar chart
    ax_bar.text(1.05, 0.95, stats_text, transform=ax_bar.transAxes, fontsize=12, color='black', va='top', ha='left', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    filename = f"offense_efficiency_analysis.png"
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(filename)
    print(f'Analysis figure saved as {filename}')
    print(stats_text)
    plt.show()

if __name__ == "__main__":
    run_simulation(150000)