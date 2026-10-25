
import streamlit as st
from collections import Counter, defaultdict, deque

# =========================================================
# NEUROCHASE — HUMAN INTELLIGENCE VS ARTIFICIAL INTELLIGENCE
# Complete Streamlit game | Python 3.12+
# =========================================================

st.set_page_config(
    page_title="NEUROCHASE | Adaptive AI Maze",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------- DESIGN -------------------------

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(ellipse at top left, #172554 0%, transparent 42%),
        radial-gradient(ellipse at bottom right, #3b0764 0%, transparent 40%),
        #070b18;
    color: #f1f5f9;
}
h1, h2, h3, p, label {
    color: #f1f5f9 !important;
}
.hero {
    padding: 24px;
    border: 1px solid #334155;
    border-radius: 20px;
    text-align: center;
    background: linear-gradient(120deg, #111c3d, #30105a, #082f49);
    margin-bottom: 18px;
}
.hero h1 {
    color: #67e8f9 !important;
    font-size: 42px;
    margin-bottom: 4px;
    text-shadow: 0 0 18px #06b6d4;
}
.hero p { color: #c4b5fd !important; }
.stat {
    background: linear-gradient(135deg, #111827, #172554);
    border: 1px solid #475569;
    border-radius: 14px;
    padding: 14px;
    text-align: center;
    margin-bottom: 8px;
}
.stat-label {
    font-size: 12px;
    color: #94a3b8;
    letter-spacing: 1px;
}
.stat-value {
    font-size: 25px;
    font-weight: 800;
    color: #67e8f9;
}
.maze {
    display: grid;
    grid-template-columns: repeat(15, minmax(0, 1fr));
    gap: 3px;
    padding: 12px;
    background: #050816;
    border: 2px solid #334155;
    border-radius: 15px;
    box-shadow: 0 0 24px #312e8155;
}
.cell {
    aspect-ratio: 1 / 1;
    min-width: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    font-size: clamp(9px, 2vw, 19px);
    font-weight: bold;
}
.wall {
    background: linear-gradient(135deg, #4338ca, #164e63);
    border: 1px solid #6366f1;
}
.path { background: #111827; }
.pellet { color: #facc15; text-shadow: 0 0 8px #facc15; }
.player {
    background: #064e3b;
    color: #6ee7b7;
    box-shadow: 0 0 12px #10b981;
}
.enemy {
    background: #4c0519;
    color: #fda4af;
    box-shadow: 0 0 12px #f43f5e;
}
.panel {
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 16px;
    background: #111827cc;
    margin-bottom: 12px;
}
div.stButton > button {
    border: 1px solid #6366f1;
    border-radius: 12px;
    min-height: 43px;
    background: linear-gradient(135deg, #312e81, #164e63);
    color: white;
    font-weight: bold;
}
div.stButton > button:hover {
    border-color: #67e8f9;
    color: #67e8f9;
}
</style>
""", unsafe_allow_html=True)

# ------------------------- MAZE --------------------------
# # = wall; . = walkable space

MAZE = [
    "###############",
    "#.............#",
    "#.###.###.###.#",
    "#.............#",
    "###.#.###.#.###",
    "#.............#",
    "#.###.###.###.#",
    "#.............#",
    "###.#.###.#.###",
    "#.............#",
    "###############",
]

ROWS = len(MAZE)
COLS = len(MAZE[0])

PLAYER_START = (1, 1)
ENEMY_START = (9, 13)

DIRECTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}

ARROWS = {
    "UP": "⬆️",
    "DOWN": "⬇️",
    "LEFT": "⬅️",
    "RIGHT": "➡️",
}

# ---------------------- GAME LOGIC -----------------------

def is_walkable(position):
    row, col = position
    return (
        0 <= row < ROWS
        and 0 <= col < COLS
        and MAZE[row][col] != "#"
    )


def create_pellets():
    """Create pellets on every walkable maze cell."""
    pellets = set()

    for row in range(ROWS):
        for col in range(COLS):
            if MAZE[row][col] != "#":
                pellets.add((row, col))

    pellets.discard(PLAYER_START)
    pellets.discard(ENEMY_START)
    return pellets


def get_neighbors(position):
    row, col = position
    neighbors = []

    for direction, (dr, dc) in DIRECTIONS.items():
        candidate = (row + dr, col + dc)

        if is_walkable(candidate):
            neighbors.append((candidate, direction))

    return neighbors


def shortest_path_step(start, target):
    """Return the first step along a shortest path using BFS."""
    if start == target:
        return start

    queue = deque([(start, None)])
    visited = {start}

    while queue:
        current, first_step = queue.popleft()

        for neighbor, _ in get_neighbors(current):
            if neighbor in visited:
                continue

            next_first_step = (
                neighbor if first_step is None else first_step
            )

            if neighbor == target:
                return next_first_step

            visited.add(neighbor)
            queue.append((neighbor, next_first_step))

    return start


def predict_next_direction(history, transition_counts):
    """
    Learn from the player's previous two moves.
    Fall back to the most frequent observed move.
    """
    if len(history) >= 2:
        context = tuple(history[-2:])
        options = transition_counts.get(context, Counter())

        if options:
            return options.most_common(1)[0][0]

    if history:
        counts = Counter(history)
        return counts.most_common(1)[0][0]

    return None


def initialize_game():
    """Initialize every state variable used by the game."""
    st.session_state.player = PLAYER_START
    st.session_state.enemy = ENEMY_START
    st.session_state.pellets = create_pellets()

    st.session_state.score = 0
    st.session_state.lives = 3
    st.session_state.round = 1

    st.session_state.move_history = []
    st.session_state.transition_counts = defaultdict(Counter)

    st.session_state.last_prediction = None
    st.session_state.predictions_total = 0
    st.session_state.predictions_correct = 0
    st.session_state.last_move = "NONE"
    st.session_state.last_ai_action = "Waiting for movement"

    st.session_state.game_over = False
    st.session_state.won = False
    st.session_state.message = "Collect the glowing pellets and avoid the AI!"

    st.session_state.initialized = True


def move_enemy():
    """The AI predicts the player's next position and chases it."""
    player = st.session_state.player
    enemy = st.session_state.enemy
    history = st.session_state.move_history
    counts = st.session_state.transition_counts
    round_number = st.session_state.round

    prediction = predict_next_direction(history, counts)

    # Aim one step ahead when the predicted step is valid.
    target = player

    if prediction in DIRECTIONS:
        dr, dc = DIRECTIONS[prediction]
        predicted_position = (player[0] + dr, player[1] + dc)

        if is_walkable(predicted_position):
            target = predicted_position

    # AI gets increasingly better at chasing in later rounds.
    # Round 1: 20%, Round 2: 40%, ... Round 5: 100%.
    prediction_chance = round_number * 0.20

    import random

    if prediction and random.random() < prediction_chance:
        target_position = target
        st.session_state.last_ai_action = (
            f"🧠 Predictive chase toward {prediction}"
        )
    else:
        target_position = player
        st.session_state.last_ai_action = "🔎 Tracking your current position"

    next_position = shortest_path_step(enemy, target_position)

    # If the AI is already at its target, take a legal step closer
    # to the player, if possible.
    if next_position == enemy:
        next_position = shortest_path_step(enemy, player)

    st.session_state.enemy = next_position


def advance_round_if_needed():
    """Start the next round when all pellets have been collected."""
    if st.session_state.pellets:
        return

    if st.session_state.round >= 5:
        st.session_state.won = True
        st.session_state.message = (
            "🏆 You defeated the adaptive AI across all five rounds!"
        )
        return

    st.session_state.round += 1
    st.session_state.player = PLAYER_START
    st.session_state.enemy = ENEMY_START
    st.session_state.pellets = create_pellets()

    st.session_state.message = (
        f"⚡ Round {st.session_state.round} started! "
        "The AI is now more predictive."
    )


def check_collision():
    """Remove one life when the enemy catches the player."""
    if st.session_state.player != st.session_state.enemy:
        return

    st.session_state.lives -= 1

    if st.session_state.lives <= 0:
        st.session_state.lives = 0
        st.session_state.game_over = True
        st.session_state.message = (
            "💀 GAME OVER! The AI caught you. Try a new strategy!"
        )
    else:
        st.session_state.player = PLAYER_START
        st.session_state.enemy = ENEMY_START
        st.session_state.message = (
            f"💥 The AI caught you! "
            f"{st.session_state.lives} life/lives remaining."
        )


def move_player(direction):
    """Move the player, update AI learning, then move the enemy."""
    if st.session_state.game_over or st.session_state.won:
        return

    if direction not in DIRECTIONS:
        return

    dr, dc = DIRECTIONS[direction]
    current = st.session_state.player
    candidate = (current[0] + dr, current[1] + dc)

    # A wall blocks movement.
    if not is_walkable(candidate):
        st.session_state.message = "🧱 A wall blocks your way!"
        return

    # Score the AI's previous prediction against the actual move.
    previous_prediction = st.session_state.last_prediction

    if previous_prediction is not None:
        st.session_state.predictions_total += 1

        if previous_prediction == direction:
            st.session_state.predictions_correct += 1

    # Learn which move follows the previous two moves.
    history = st.session_state.move_history

    if len(history) >= 2:
        context = tuple(history[-2:])
        st.session_state.transition_counts[context][direction] += 1

    history.append(direction)

    # Keep history bounded while retaining enough recent context.
    if len(history) > 1000:
        del history[:200]

    st.session_state.player = candidate
    st.session_state.last_move = direction

    # Collect a pellet.
    if candidate in st.session_state.pellets:
        st.session_state.pellets.remove(candidate)
        st.session_state.score += 10

    # Store the AI's prediction for the player's next move.
    st.session_state.last_prediction = predict_next_direction(
        history, st.session_state.transition_counts
    )

    advance_round_if_needed()

    if st.session_state.won:
        return

    move_enemy()
    check_collision()

# --------------------- INITIALIZATION --------------------

if not st.session_state.get("initialized", False):
    initialize_game()

# -------------------------- HEADER -----------------------

st.markdown("""
<div class="hero">
    <h1>🧠 NEUROCHASE</h1>
    <p>HUMAN INTELLIGENCE vs ARTIFICIAL INTELLIGENCE</p>
    <div>⚡ THINK FAST &nbsp; • &nbsp; 🌀 CHANGE YOUR STRATEGY
    &nbsp; • &nbsp; 🤖 OUTSMART THE AI</div>
</div>
""", unsafe_allow_html=True)

# ---------------------- GAME STATUS ----------------------

if st.session_state.game_over:
    st.error(
        f"💀 GAME OVER — Final score: {st.session_state.score}. "
        "Press Restart Game to play again."
    )
elif st.session_state.won:
    st.success(
        f"🏆 VICTORY! You completed all 5 rounds! "
        f"Final score: {st.session_state.score}."
    )
else:
    st.info(st.session_state.message)

accuracy = (
    100 * st.session_state.predictions_correct
    / st.session_state.predictions_total
    if st.session_state.predictions_total
    else 0
)

stats = st.columns(5)

stat_values = [
    ("SCORE", st.session_state.score),
    ("LIVES", "❤️ " * st.session_state.lives or "💔"),
    ("ROUND", f"{st.session_state.round}/5"),
    ("PELLETS LEFT", len(st.session_state.pellets)),
    ("AI ACCURACY", f"{accuracy:.0f}%"),
]

for column, (label, value) in zip(stats, stat_values):
    column.markdown(
        f"""
        <div class="stat">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------- MAIN LAYOUT ---------------------

game_column, ai_column = st.columns([1.8, 1])

with game_column:
    st.subheader("🎮 THE NEON MAZE")

    # Render the maze as an HTML grid.
    # All positions are checked against the fixed maze.
    cells = []

    for row in range(ROWS):
        for col in range(COLS):
            position = (row, col)

            if MAZE[row][col] == "#":
                cells.append('<div class="cell wall">◆</div>')
            elif position == st.session_state.player:
                cells.append('<div class="cell player">🟡</div>')
            elif position == st.session_state.enemy:
                cells.append('<div class="cell enemy">🤖</div>')
            elif position in st.session_state.pellets:
                cells.append('<div class="cell path pellet">•</div>')
            else:
                cells.append('<div class="cell path"></div>')

    st.markdown(
        '<div class="maze">' + "".join(cells) + '</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "🟡 You  |  🤖 Adaptive AI  |  🟡 • Pellets  |  "
        "🔷 Walls"
    )

    st.subheader("🕹️ MOVEMENT CONTROLS")

    # Button controls work on desktop and mobile.
    # Streamlit reruns the script when a button is clicked.
    control_top = st.columns([1, 1, 1])

    with control_top[1]:
        if st.button("⬆️ UP", use_container_width=True):
            move_player("UP")
            st.rerun()

    control_middle = st.columns([1, 1, 1])

    with control_middle[0]:
        if st.button("⬅️ LEFT", use_container_width=True):
            move_player("LEFT")
            st.rerun()

    with control_middle[1]:
        if st.button("⬇️ DOWN", use_container_width=True):
            move_player("DOWN")
            st.rerun()

    with control_middle[2]:
        if st.button("➡️ RIGHT", use_container_width=True):
            move_player("RIGHT")
            st.rerun()

    if st.button("🔄 RESTART GAME", use_container_width=True):
        initialize_game()
        st.rerun()

with ai_column:
    st.subheader("🧠 AI BRAIN")

    prediction = st.session_state.last_prediction

    if prediction:
        prediction_text = f"{ARROWS[prediction]} {prediction}"
    else:
        prediction_text = "Learning your moves..."

    st.markdown(
        f"""
        <div class="panel">
            <h3>🔮 Next-Move Prediction</h3>
            <div style="font-size:25px;color:#67e8f9;font-weight:800;">
                {prediction_text}
            </div>
            <p>The AI learns from the sequence of your moves.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="panel">
            <h3>🤖 AI Status</h3>
            <p>{st.session_state.last_ai_action}</p>
            <p><b>Difficulty:</b> Round {st.session_state.round} of 5</p>
            <p><b>Moves observed:</b> {len(st.session_state.move_history)}</p>
            <p><b>Predictions evaluated:</b>
            {st.session_state.predictions_total}</p>
            <p><b>Correct predictions:</b>
            {st.session_state.predictions_correct}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div class="panel">
        <h3>⚙️ HOW TO PLAY</h3>
        <p>1. Use the four direction buttons to move.</p>
        <p>2. Collect pellets to earn 10 points each.</p>
        <p>3. Avoid the AI enemy.</p>
        <p>4. You have only 3 lives.</p>
        <p>5. Complete all 5 rounds to win.</p>
        <p>6. Change your movement patterns to confuse the AI.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#94a3b8;'>"
    "NEUROCHASE • ADAPTIVE AI MAZE • BUILT WITH PYTHON & STREAMLIT"
    "</p>",
    unsafe_allow_html=True,
)
