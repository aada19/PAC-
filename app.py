import streamlit as st
import streamlit_hotkeys as hotkeys
from collections import Counter, defaultdict, deque
import random

# ============================================================
# NEUROCHASE
# HUMAN INTELLIGENCE VS ARTIFICIAL INTELLIGENCE
# ============================================================

st.set_page_config(
    page_title="NEUROCHASE - Adaptive AI Game",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(circle at 10% 10%, #172554 0%, transparent 35%),
            radial-gradient(circle at 90% 90%, #3b0764 0%, transparent 35%),
            #050816;
        color: white;
    }

    .hero {
        padding: 24px;
        border-radius: 22px;
        text-align: center;
        margin-bottom: 18px;
        background: linear-gradient(
            135deg,
            #111827,
            #312e81,
            #164e63,
            #4c1d95
        );
        border: 2px solid #6366f1;
        box-shadow: 0 0 30px #4f46e555;
    }

    .hero h1 {
        color: #67e8f9 !important;
        font-size: 44px;
        font-weight: 900;
        margin-bottom: 5px;
        text-shadow: 0 0 20px #06b6d4;
    }

    .hero p {
        color: #c4b5fd !important;
        font-size: 18px;
        font-weight: 700;
        letter-spacing: 2px;
    }

    .stat {
        background: linear-gradient(135deg, #111827, #172554);
        border: 1px solid #475569;
        border-radius: 15px;
        padding: 12px;
        text-align: center;
        margin-bottom: 10px;
    }

    .stat-label {
        font-size: 11px;
        color: #94a3b8;
        letter-spacing: 1px;
        font-weight: 700;
    }

    .stat-value {
        font-size: 23px;
        font-weight: 900;
        color: #67e8f9;
    }

    .panel {
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 17px;
        background: rgba(17, 24, 39, 0.88);
        margin-bottom: 13px;
    }

    .panel-title {
        color: #67e8f9;
        font-size: 20px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .prediction {
        color: #facc15;
        font-size: 27px;
        font-weight: 900;
        text-align: center;
        padding: 10px;
    }

    .maze {
        display: grid;
        grid-template-columns: repeat(15, minmax(0, 1fr));
        gap: 3px;
        padding: 12px;
        border-radius: 17px;
        background: #020617;
        border: 2px solid #4338ca;
        box-shadow:
            0 0 20px rgba(99, 102, 241, 0.35),
            inset 0 0 25px rgba(30, 41, 59, 0.8);
    }

    .cell {
        aspect-ratio: 1 / 1;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 5px;
        font-size: clamp(8px, 2vw, 18px);
        font-weight: 900;
    }

    .wall {
        background: linear-gradient(135deg, #3730a3, #164e63);
        border: 1px solid #6366f1;
        color: #a5b4fc;
    }

    .path {
        background: #0f172a;
    }

    .pellet {
        color: #facc15;
        text-shadow: 0 0 9px #facc15;
        font-size: 21px;
    }

    .player {
        background: radial-gradient(circle, #065f46, #064e3b);
        color: #fde047;
        box-shadow: 0 0 15px #10b981;
        border: 1px solid #34d399;
    }

    .enemy {
        background: radial-gradient(circle, #881337, #4c0519);
        color: #fb7185;
        box-shadow: 0 0 15px #f43f5e;
        border: 1px solid #fb7185;
    }

    .exit {
        background: radial-gradient(circle, #854d0e, #713f12);
        color: #fde047;
        border: 2px solid #facc15;
        box-shadow: 0 0 18px #facc15;
        font-size: clamp(9px, 2vw, 20px);
    }

    .keyboard {
        text-align: center;
        padding: 13px;
        border-radius: 13px;
        background: #111827;
        border: 1px solid #334155;
        margin-top: 12px;
        color: #c4b5fd;
        font-weight: 700;
    }

    div.stButton > button {
        border: 1px solid #6366f1;
        border-radius: 12px;
        min-height: 43px;
        background: linear-gradient(135deg, #312e81, #164e63);
        color: white;
        font-weight: 800;
    }

    div.stButton > button:hover {
        border-color: #67e8f9;
        color: #67e8f9;
        box-shadow: 0 0 12px #06b6d455;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# MAZE
# ============================================================

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

# EXIT FOR EVERY ROUND
EXIT_POSITION = (9, 13)

DIRECTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}

ARROWS = {
    "UP": "⬆️ UP",
    "DOWN": "⬇️ DOWN",
    "LEFT": "⬅️ LEFT",
    "RIGHT": "➡️ RIGHT",
}

# ============================================================
# BASIC FUNCTIONS
# ============================================================

def is_walkable(position):
    row, col = position

    if row < 0 or row >= ROWS:
        return False

    if col < 0 or col >= COLS:
        return False

    return MAZE[row][col] != "#"


def create_pellets():
    """
    Create pellets on walkable cells.

    The EXIT is not given a pellet so that it remains
    clearly visible to the player.
    """

    pellets = set()

    for row in range(ROWS):
        for col in range(COLS):

            position = (row, col)

            if MAZE[row][col] != "#":
                if position != PLAYER_START:
                    if position != EXIT_POSITION:
                        pellets.add(position)

    return pellets


def get_neighbors(position):

    row, col = position

    neighbors = []

    for direction, movement in DIRECTIONS.items():

        dr, dc = movement

        new_position = (
            row + dr,
            col + dc
        )

        if is_walkable(new_position):

            neighbors.append(
                (new_position, direction)
            )

    return neighbors


# ============================================================
# BFS PATHFINDING
# ============================================================

def shortest_path_step(start, target):

    if start == target:
        return start

    queue = deque()

    queue.append(
        (start, None)
    )

    visited = {start}

    while queue:

        current, first_step = queue.popleft()

        for neighbor, direction in get_neighbors(current):

            if neighbor in visited:
                continue

            if first_step is None:
                next_first_step = neighbor
            else:
                next_first_step = first_step

            if neighbor == target:

                return next_first_step

            visited.add(neighbor)

            queue.append(
                (neighbor, next_first_step)
            )

    return start


# ============================================================
# AI LEARNING
# ============================================================

def predict_next_direction():

    history = st.session_state.move_history

    transitions = st.session_state.transition_counts

    # Learn from the previous two moves.

    if len(history) >= 2:

        context = (
            history[-2],
            history[-1]
        )

        options = transitions.get(
            context,
            Counter()
        )

        if options:

            return options.most_common(1)[0][0]

    # If there isn't enough sequence data,
    # use the most common movement.

    if history:

        counts = Counter(history)

        return counts.most_common(1)[0][0]

    return None


# ============================================================
# INITIALIZE GAME
# ============================================================

def initialize_game():

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

    st.session_state.last_ai_action = (
        "Waiting for your first move..."
    )

    st.session_state.message = (
        "Find the 🚪 EXIT before the AI catches you!"
    )

    st.session_state.game_over = False

    st.session_state.won = False

    st.session_state.initialized = True


# ============================================================
# ROUND COMPLETION
# ============================================================

def complete_round():

    current_round = st.session_state.round

    # FINAL ROUND
    if current_round >= 5:

        st.session_state.won = True

        st.session_state.message = (
            "🏆 VICTORY! "
            "You escaped all 5 rounds and defeated the AI!"
        )

        return

    # NEXT ROUND
    st.session_state.round += 1

    st.session_state.player = PLAYER_START

    st.session_state.enemy = ENEMY_START

    st.session_state.pellets = create_pellets()

    st.session_state.last_prediction = None

    st.session_state.message = (
        f"🚪 EXIT FOUND! "
        f"ROUND {st.session_state.round} STARTED! "
        f"The AI is now smarter."
    )


# ============================================================
# COLLISION
# ============================================================

def check_collision():

    if st.session_state.player != st.session_state.enemy:
        return

    st.session_state.lives -= 1

    if st.session_state.lives <= 0:

        st.session_state.lives = 0

        st.session_state.game_over = True

        st.session_state.message = (
            "💀 GAME OVER! "
            "The AI learned your movement pattern."
        )

    else:

        st.session_state.player = PLAYER_START

        st.session_state.enemy = ENEMY_START

        st.session_state.message = (
            "💥 CAUGHT BY THE AI! "
            f"You have {st.session_state.lives} lives left."
        )


# ============================================================
# AI MOVEMENT
# ============================================================

def move_enemy():

    player = st.session_state.player

    enemy = st.session_state.enemy

    prediction = predict_next_direction()

    round_number = st.session_state.round

    # AI gets smarter every round.

    prediction_probability = round_number * 0.20

    predicted_target = player

    if prediction in DIRECTIONS:

        dr, dc = DIRECTIONS[prediction]

        predicted_position = (
            player[0] + dr,
            player[1] + dc
        )

        if is_walkable(predicted_position):

            predicted_target = predicted_position

    if (
        prediction is not None
        and random.random() < prediction_probability
    ):

        target = predicted_target

        st.session_state.last_ai_action = (
            "🧠 AI is predicting your next move: "
            f"{ARROWS[prediction]}"
        )

    else:

        target = player

        st.session_state.last_ai_action = (
            "👁️ AI is tracking your current position"
        )

    new_enemy_position = shortest_path_step(
        enemy,
        target
    )

    st.session_state.enemy = new_enemy_position


# ============================================================
# PLAYER MOVEMENT
# ============================================================

def move_player(direction):

    if st.session_state.game_over:
        return

    if st.session_state.won:
        return

    if direction not in DIRECTIONS:
        return

    # Check the previous AI prediction.

    previous_prediction = (
        st.session_state.last_prediction
    )

    if previous_prediction is not None:

        st.session_state.predictions_total += 1

        if previous_prediction == direction:

            st.session_state.predictions_correct += 1

    # Learn movement sequence.

    history = st.session_state.move_history

    if len(history) >= 2:

        context = (
            history[-2],
            history[-1]
        )

        st.session_state.transition_counts[
            context
        ][direction] += 1

    history.append(direction)

    if len(history) > 1000:

        del history[:200]

    # Calculate player movement.

    row, col = st.session_state.player

    dr, dc = DIRECTIONS[direction]

    new_position = (
        row + dr,
        col + dc
    )

    # Wall collision.

    if not is_walkable(new_position):

        st.session_state.message = (
            "🧱 WALL! Choose another direction."
        )

        return

    # Move player.

    st.session_state.player = new_position

    st.session_state.last_move = direction

    # Collect pellet.

    if new_position in st.session_state.pellets:

        st.session_state.pellets.remove(
            new_position
        )

        st.session_state.score += 10

        st.session_state.message = (
            "⭐ Pellet collected! +10 points"
        )

    # ========================================================
    # CHECK EXIT
    # ========================================================

    if new_position == EXIT_POSITION:

        # Bonus for reaching exit.

        st.session_state.score += 100

        complete_round()

        return

    # AI prediction for next move.

    st.session_state.last_prediction = (
        predict_next_direction()
    )

    # AI movement.

    move_enemy()

    # Collision check.

    check_collision()


# ============================================================
# INITIALIZE
# ============================================================

if not st.session_state.get(
    "initialized",
    False
):

    initialize_game()


# ============================================================
# KEYBOARD CONTROLS
# ============================================================
# Arrow keys:
#
# ↑ ArrowUp
# ↓ ArrowDown
# ← ArrowLeft
# → ArrowRight
#
# prevent_default stops the browser from scrolling.
# ============================================================

hotkeys.activate(
    [
        hotkeys.hk(
            "move_up",
            "ArrowUp",
            prevent_default=True,
            ignore_repeat=True,
            help="Move Up"
        ),

        hotkeys.hk(
            "move_down",
            "ArrowDown",
            prevent_default=True,
            ignore_repeat=True,
            help="Move Down"
        ),

        hotkeys.hk(
            "move_left",
            "ArrowLeft",
            prevent_default=True,
            ignore_repeat=True,
            help="Move Left"
        ),

        hotkeys.hk(
            "move_right",
            "ArrowRight",
            prevent_default=True,
            ignore_repeat=True,
            help="Move Right"
        ),
    ],
    key="neurochase_controls"
)


# ============================================================
# PROCESS KEYBOARD INPUT
# ============================================================

if hotkeys.pressed(
    "move_up",
    key="neurochase_controls"
):

    move_player("UP")

    st.rerun()


if hotkeys.pressed(
    "move_down",
    key="neurochase_controls"
):

    move_player("DOWN")

    st.rerun()


if hotkeys.pressed(
    "move_left",
    key="neurochase_controls"
):

    move_player("LEFT")

    st.rerun()


if hotkeys.pressed(
    "move_right",
    key="neurochase_controls"
):

    move_player("RIGHT")

    st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <h1>🧠 NEUROCHASE</h1>

        <p>
            HUMAN INTELLIGENCE VS ARTIFICIAL INTELLIGENCE
        </p>

        <div>
            ⚡ THINK FAST
            &nbsp; • &nbsp;
            🌀 CHANGE YOUR STRATEGY
            &nbsp; • &nbsp;
            🤖 OUTSMART THE AI
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# STATUS MESSAGE
# ============================================================

if st.session_state.game_over:

    st.error(
        f"💀 GAME OVER! "
        f"Final Score: {st.session_state.score}"
    )

elif st.session_state.won:

    st.success(
        f"🏆 NEUROCHASE MASTER! "
        f"Final Score: {st.session_state.score}"
    )

else:

    st.info(
        st.session_state.message
    )


# ============================================================
# STATISTICS
# ============================================================

if st.session_state.predictions_total > 0:

    accuracy = (
        st.session_state.predictions_correct
        /
        st.session_state.predictions_total
        * 100
    )

else:

    accuracy = 0


stats = st.columns(5)

stat_data = [

    (
        "SCORE",
        str(st.session_state.score)
    ),

    (
        "LIVES",
        "❤️ " * st.session_state.lives
    ),

    (
        "ROUND",
        f"{st.session_state.round}/5"
    ),

    (
        "PELLETS",
        str(len(st.session_state.pellets))
    ),

    (
        "AI ACCURACY",
        f"{accuracy:.0f}%"
    ),
]


for column, (label, value) in zip(
    stats,
    stat_data
):

    column.markdown(
        f"""
        <div class="stat">

            <div class="stat-label">
                {label}
            </div>

            <div class="stat-value">
                {value}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MAIN GAME
# ============================================================

game_column, ai_column = st.columns(
    [1.8, 1]
)


# ============================================================
# MAZE DISPLAY
# ============================================================

with game_column:

    st.subheader(
        f"🎮 ROUND {st.session_state.round} — FIND THE EXIT"
    )

    cells = []

    for row in range(ROWS):

        for col in range(COLS):

            position = (
                row,
                col
            )

            # WALL

            if MAZE[row][col] == "#":

                cells.append(
                    '<div class="cell wall">◆</div>'
                )

            # EXIT

            elif position == EXIT_POSITION:

                cells.append(
                    '<div class="cell exit">🚪</div>'
                )

            # PLAYER

            elif (
                position
                ==
                st.session_state.player
            ):

                cells.append(
                    '<div class="cell player">🟡</div>'
                )

            # AI

            elif (
                position
                ==
                st.session_state.enemy
            ):

                cells.append(
                    '<div class="cell enemy">🤖</div>'
                )

            # PELLET

            elif (
                position
                in
                st.session_state.pellets
            ):

                cells.append(
                    '<div class="cell path pellet">•</div>'
                )

            # EMPTY

            else:

                cells.append(
                    '<div class="cell path"></div>'
                )


    st.markdown(
        '<div class="maze">'
        + "".join(cells)
        + '</div>',
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="keyboard">

            ⌨️ <b>KEYBOARD CONTROLS ENABLED</b>

            <br><br>

            Use
            <b>⬆️ UP</b>,
            <b>⬇️ DOWN</b>,
            <b>⬅️ LEFT</b>
            and
            <b>➡️ RIGHT</b>
            arrow keys.

            <br><br>

            🚪 <b>Reach the EXIT to finish the round!</b>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.caption(
        "🟡 YOU  |  🤖 AI  |  ⭐ PELLET  |  "
        "🚪 EXIT  |  🔷 WALL"
    )


# ============================================================
# BACKUP BUTTON CONTROLS
# ============================================================

    st.subheader(
        "🕹️ BACKUP CONTROLS"
    )

    top_buttons = st.columns(3)

    with top_buttons[1]:

        if st.button(
            "⬆️ UP",
            use_container_width=True
        ):

            move_player("UP")

            st.rerun()


    middle_buttons = st.columns(3)

    with middle_buttons[0]:

        if st.button(
            "⬅️ LEFT",
            use_container_width=True
        ):

            move_player("LEFT")

            st.rerun()


    with middle_buttons[1]:

        if st.button(
            "⬇️ DOWN",
            use_container_width=True
        ):

            move_player("DOWN")

            st.rerun()


    with middle_buttons[2]:

        if st.button(
            "➡️ RIGHT",
            use_container_width=True
        ):

            move_player("RIGHT")

            st.rerun()


    st.write("")


    if st.button(
        "🔄 RESTART GAME",
        use_container_width=True
    ):

        initialize_game()

        st.rerun()


# ============================================================
# AI BRAIN
# ============================================================

with ai_column:

    st.subheader(
        "🧠 AI BRAIN"
    )


    prediction = (
        st.session_state.last_prediction
    )


    if prediction:

        prediction_text = ARROWS[prediction]

    else:

        prediction_text = (
            "Learning..."
        )


    st.markdown(
        f"""
        <div class="panel">

            <div class="panel-title">
                🔮 NEXT-MOVE PREDICTION
            </div>

            <div class="prediction">
                {prediction_text}
            </div>

            <p>
                The AI studies the sequence of
                your previous movements.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        f"""
        <div class="panel">

            <div class="panel-title">
                🤖 AI STATUS
            </div>

            <p>
                {st.session_state.last_ai_action}
            </p>

            <p>
                <b>Round:</b>
                {st.session_state.round}/5
            </p>

            <p>
                <b>Moves learned:</b>
                {len(st.session_state.move_history)}
            </p>

            <p>
                <b>Predictions tested:</b>
                {st.session_state.predictions_total}
            </p>

            <p>
                <b>Correct predictions:</b>
                {st.session_state.predictions_correct}
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="panel">

            <div class="panel-title">
                🚪 ROUND OBJECTIVE
            </div>

            <p>
                Find the glowing
                <b>🚪 EXIT</b>
                before the AI catches you.
            </p>

            <p>
                ⭐ Pellets give
                <b>+10 points</b>.
            </p>

            <p>
                🚪 Reaching the exit gives
                <b>+100 points</b>.
            </p>

            <p>
                Completing the exit in
                Round 5 means
                <b>VICTORY!</b>
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="panel">

            <div class="panel-title">
                ⚙️ HOW TO PLAY
            </div>

            <p>
                1️⃣ Move using the arrow keys.
            </p>

            <p>
                2️⃣ Collect ⭐ pellets.
            </p>

            <p>
                3️⃣ Avoid the 🤖 AI.
            </p>

            <p>
                4️⃣ You have ❤️ 3 lives.
            </p>

            <p>
                5️⃣ Find 🚪 the exit.
            </p>

            <p>
                6️⃣ Complete all 5 rounds.
            </p>

            <p>
                7️⃣ Change your movement pattern
                to confuse the AI.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <p style="
        text-align:center;
        color:#64748b;
        font-weight:700;
        letter-spacing:1px;
    ">
        NEUROCHASE • ADAPTIVE AI MAZE
        • BUILT WITH PYTHON & STREAMLIT
    </p>
    """,
    unsafe_allow_html=True
)
