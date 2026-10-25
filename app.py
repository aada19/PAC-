import streamlit as st
import random
import time
from collections import Counter, deque

# ============================================================
# NEUROCHASE
# Human Intelligence vs Artificial Intelligence
# Pac-Man Inspired Adaptive AI Game
# ============================================================

st.set_page_config(
    page_title="NEUROCHASE | Human vs AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 10% 10%, #172554 0%, transparent 30%),
        radial-gradient(circle at 90% 10%, #3b0764 0%, transparent 28%),
        radial-gradient(circle at 50% 100%, #064e3b 0%, transparent 30%),
        #030712;
    color: white;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Main title */

.neuro-title {
    text-align: center;
    font-size: 54px;
    font-weight: 1000;
    letter-spacing: 8px;
    margin-bottom: 0;
    background: linear-gradient(
        90deg,
        #00eaff,
        #7c3aed,
        #ff2bd6,
        #00ffa3
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.neuro-subtitle {
    text-align: center;
    color: #9ca3af;
    letter-spacing: 4px;
    font-size: 13px;
    margin-bottom: 25px;
}

/* Cards */

.neuro-card {
    background: linear-gradient(
        145deg,
        rgba(15,23,42,.95),
        rgba(15,23,42,.70)
    );
    border: 1px solid rgba(56,189,248,.22);
    border-radius: 20px;
    padding: 18px;
    box-shadow:
        0 0 25px rgba(0,234,255,.05),
        inset 0 0 25px rgba(124,58,237,.03);
    margin-bottom: 15px;
}

.card-title {
    color: #67e8f9;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

/* Stats */

.stat-box {
    background: rgba(255,255,255,.035);
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 14px;
    padding: 12px;
    text-align: center;
}

.stat-number {
    font-size: 28px;
    font-weight: 900;
}

.stat-label {
    font-size: 10px;
    color: #94a3b8;
    letter-spacing: 1px;
}

/* AI */

.ai-panel {
    border: 1px solid rgba(168,85,247,.35);
    background:
        radial-gradient(
            circle at top right,
            rgba(168,85,247,.15),
            transparent 50%
        ),
        rgba(15,23,42,.95);
}

.learning {
    height: 12px;
    border-radius: 20px;
    background: #111827;
    overflow: hidden;
    margin-top: 8px;
}

.learning-fill {
    height: 100%;
    background: linear-gradient(
        90deg,
        #00eaff,
        #7c3aed,
        #ff2bd6
    );
    border-radius: 20px;
}

/* Messages */

.game-message {
    text-align: center;
    padding: 15px;
    border-radius: 15px;
    font-size: 18px;
    font-weight: 800;
    background: rgba(124,58,237,.12);
    border: 1px solid rgba(168,85,247,.25);
    margin: 15px 0;
}

.legend {
    color: #cbd5e1;
    font-size: 13px;
    line-height: 2;
}

/* Buttons */

.stButton > button {
    border-radius: 12px;
    font-weight: 900;
    border: 1px solid rgba(56,189,248,.25);
    background: linear-gradient(
        135deg,
        #075985,
        #4c1d95
    );
    color: white;
}

.stButton > button:hover {
    border-color: #22d3ee;
    color: white;
    box-shadow: 0 0 18px rgba(34,211,238,.25);
}

/* Instructions */

.instruction {
    text-align: center;
    color: #94a3b8;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# MAZE
# ============================================================

MAZE = [
    "#####################",
    "#         #         #",
    "# ### ### # ### ### #",
    "# #     #   #     # #",
    "# # ### ##### ### # #",
    "#     #       #     #",
    "##### # ##### # #####",
    "#       #   #       #",
    "# ### # # # # # ### #",
    "# #   #   #   #   # #",
    "# ### ######### ### #",
    "#     #       #     #",
    "##### # ##### # #####",
    "# #     #   #     # #",
    "# ### ### # ### ### #",
    "#         #         #",
    "#####################"
]

ROWS = len(MAZE)
COLS = len(MAZE[0])


# ============================================================
# SESSION STATE
# ============================================================

def initialize_game():

    st.session_state.player = [1, 1]

    st.session_state.ai = [COLS - 2, ROWS - 2]

    st.session_state.lives = 3

    st.session_state.score = 0

    st.session_state.experience = 0

    st.session_state.round = 1

    st.session_state.game_over = False

    st.session_state.finished = False

    st.session_state.message = (
        "🎮 ROUND 1 — COLLECT THE CORES AND ESCAPE THE AI!"
    )

    st.session_state.history = []

    st.session_state.learning = {
        "UP": 0,
        "DOWN": 0,
        "LEFT": 0,
        "RIGHT": 0
    }

    st.session_state.last_prediction = "ANALYZING..."

    st.session_state.correct_predictions = 0

    st.session_state.total_predictions = 0

    st.session_state.last_direction = "RIGHT"

    st.session_state.ai_speed = 1

    st.session_state.power = False

    st.session_state.power_timer = 0

    st.session_state.pellets = create_pellets()

    st.session_state.power_cores = [
        [1, ROWS - 2],
        [COLS - 2, 1]
    ]


if "player" not in st.session_state:
    initialize_game()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

DIRECTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1)
}


def is_wall(row, col):

    if row < 0 or row >= ROWS:
        return True

    if col < 0 or col >= COLS:
        return True

    return MAZE[row][col] == "#"


def valid_moves(position):

    row, col = position

    moves = []

    for name, (dr, dc) in DIRECTIONS.items():

        nr = row + dr
        nc = col + dc

        if not is_wall(nr, nc):
            moves.append(name)

    return moves


def move_position(position, direction):

    dr, dc = DIRECTIONS[direction]

    nr = position[0] + dr
    nc = position[1] + dc

    if not is_wall(nr, nc):
        return [nr, nc]

    return position.copy()


def create_pellets():

    pellets = []

    for r in range(ROWS):

        for c in range(COLS):

            if MAZE[r][c] == "#":
                continue

            if [r, c] == [1, 1]:
                continue

            if [r, c] == [ROWS - 2, COLS - 2]:
                continue

            if random.random() < 0.55:
                pellets.append([r, c])

    return pellets


# ============================================================
# AI LEARNING SYSTEM
# ============================================================

def learn_from_player(direction):

    """
    AI learning system.

    Every movement made by the player is stored.
    The AI builds a frequency-based behavioural model.
    """

    st.session_state.history.append(direction)

    st.session_state.learning[direction] += 1

    st.session_state.experience += 1

    # Keep recent behaviour most important
    if len(st.session_state.history) > 80:
        st.session_state.history.pop(0)


def predict_player_move():

    history = st.session_state.history

    if len(history) < 3:
        return "ANALYZING..."

    recent = history[-15:]

    counts = Counter(recent)

    prediction = counts.most_common(1)[0][0]

    return prediction


# ============================================================
# AI PATH / DECISION SYSTEM
# ============================================================

def distance(a, b):

    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def ai_choose_move():

    ai = st.session_state.ai

    player = st.session_state.player

    possible = valid_moves(ai)

    if not possible:
        return None

    prediction = predict_player_move()

    # --------------------------------------------------------
    # EARLY LEVELS
    # --------------------------------------------------------

    if st.session_state.round == 1:

        # AI behaves mostly randomly
        return random.choice(possible)

    # --------------------------------------------------------
    # LEVEL 2
    # --------------------------------------------------------

    if st.session_state.round == 2:

        if prediction in possible and random.random() < 0.45:
            return prediction

        return min(
            possible,
            key=lambda d: distance(
                move_position(ai, d),
                player
            )
        )

    # --------------------------------------------------------
    # LEVEL 3
    # --------------------------------------------------------

    if st.session_state.round == 3:

        if prediction in possible and random.random() < 0.65:
            return prediction

        return min(
            possible,
            key=lambda d: distance(
                move_position(ai, d),
                player
            )
        )

    # --------------------------------------------------------
    # LEVEL 4
    # --------------------------------------------------------

    if st.session_state.round == 4:

        if prediction in possible and random.random() < 0.78:
            return prediction

        return min(
            possible,
            key=lambda d: distance(
                move_position(ai, d),
                player
            )
        )

    # --------------------------------------------------------
    # LEVEL 5
    # --------------------------------------------------------

    if st.session_state.round == 5:

        # Highly adaptive AI
        if prediction in possible and random.random() < 0.90:
            return prediction

        return min(
            possible,
            key=lambda d: distance(
                move_position(ai, d),
                player
            )
        )


# ============================================================
# RESET POSITIONS AFTER HIT
# ============================================================

def reset_positions():

    st.session_state.player = [1, 1]

    st.session_state.ai = [
        COLS - 2,
        ROWS - 2
    ]

    st.session_state.power = False

    st.session_state.power_timer = 0


# ============================================================
# HANDLE PLAYER MOVE
# ============================================================

def player_move(direction):

    if st.session_state.game_over:
        return

    if st.session_state.finished:
        return

    st.session_state.last_direction = direction

    new_position = move_position(
        st.session_state.player,
        direction
    )

    if new_position != st.session_state.player:

        st.session_state.player = new_position

        learn_from_player(direction)

        collect_items()

        # AI predicts after seeing the movement
        st.session_state.last_prediction = predict_player_move()


# ============================================================
# COLLECT ITEMS
# ============================================================

def collect_items():

    player = st.session_state.player

    # Normal pellets
    if player in st.session_state.pellets:

        st.session_state.pellets.remove(player)

        st.session_state.score += 10

    # Power core
    if player in st.session_state.power_cores:

        st.session_state.power_cores.remove(player)

        st.session_state.score += 50

        st.session_state.power = True

        st.session_state.power_timer = 5

        st.session_state.message = (
            "⚡ POWER CORE ACTIVATED! THE AI IS VULNERABLE!"
        )


# ============================================================
# AI TURN
# ============================================================

def ai_move():

    if st.session_state.game_over:
        return

    if st.session_state.finished:
        return

    direction = ai_choose_move()

    if direction is None:
        return

    st.session_state.ai = move_position(
        st.session_state.ai,
        direction
    )

    # Prediction evaluation
    prediction = predict_player_move()

    if prediction != "ANALYZING":

        st.session_state.total_predictions += 1

        if prediction == st.session_state.last_direction:

            st.session_state.correct_predictions += 1


# ============================================================
# COLLISION
# ============================================================

def check_collision():

    player = st.session_state.player

    ai = st.session_state.ai

    if player != ai:
        return

    # Player catches AI using power
    if st.session_state.power:

        st.session_state.score += 100

        st.session_state.experience += 5

        st.session_state.ai = [
            COLS - 2,
            ROWS - 2
        ]

        st.session_state.message = (
            "💥 AMAZING! YOU OUTSMARTED THE AI!"
        )

        return

    # AI catches player
    st.session_state.lives -= 1

    if st.session_state.lives <= 0:

        st.session_state.game_over = True

        st.session_state.message = (
            "💀 GAME OVER — THE AI LEARNED YOUR PATTERN!"
        )

        return

    st.session_state.message = (
        f"💥 CAUGHT! {st.session_state.lives} LIVES REMAIN."
    )

    reset_positions()


# ============================================================
# ROUND PROGRESSION
# ============================================================

def check_round_complete():

    if len(st.session_state.pellets) == 0:

        if st.session_state.round >= 5:

            st.session_state.finished = True

            st.session_state.message = (
                "🏆 NEUROCHASE COMPLETE! "
                "YOU SURVIVED ALL 5 AI ROUNDS!"
            )

            return

        st.session_state.round += 1

        st.session_state.score += (
            250 * st.session_state.round
        )

        reset_positions()

        st.session_state.pellets = create_pellets()

        st.session_state.power_cores = [
            [1, ROWS - 2],
            [COLS - 2, 1]
        ]

        st.session_state.message = (
            f"🔥 ROUND {st.session_state.round} "
            f"UNLOCKED — THE AI IS GETTING SMARTER!"
        )


# ============================================================
# GAME TURN
# ============================================================

def perform_turn(direction):

    player_move(direction)

    ai_move()

    check_collision()

    check_round_complete()


# ============================================================
# DRAW MAZE
# ============================================================

def draw_maze():

    html = """
    <div style="
        background:
        radial-gradient(circle at 50% 40%, #101b4a, #050816 70%);
        border:2px solid #22d3ee;
        border-radius:22px;
        padding:15px;
        box-shadow:
        0 0 30px rgba(34,211,238,.20),
        inset 0 0 40px rgba(124,58,237,.12);
        overflow:auto;
    ">

    <div style="
        display:grid;
        grid-template-columns:repeat(""" + str(COLS) + """, 28px);
        gap:2px;
        justify-content:center;
    ">
    """

    for r in range(ROWS):

        for c in range(COLS):

            cell = MAZE[r][c]

            # WALL
            if cell == "#":

                html += """
                <div style="
                    width:28px;
                    height:28px;
                    border-radius:7px;
                    background:
                    linear-gradient(135deg,#172554,#312e81);
                    border:1px solid #4c1d95;
                    box-shadow:
                    0 0 7px rgba(124,58,237,.45);
                "></div>
                """

            else:

                content = ""

                # Player
                if [r, c] == st.session_state.player:

                    content = """
                    <div style="
                        width:22px;
                        height:22px;
                        border-radius:50%;
                        background:
                        radial-gradient(circle at 35% 30%,
                        #ffffff,#00eaff 35%,#2563eb);
                        box-shadow:
                        0 0 18px #00eaff;
                        border:2px solid #a5f3fc;
                    "></div>
                    """

                # AI
                elif [r, c] == st.session_state.ai:

                    ai_color = (
                        "#22c55e"
                        if st.session_state.power
                        else "#ff2bd6"
                    )

                    content = f"""
                    <div style="
                        width:22px;
                        height:22px;
                        border-radius:8px;
                        background:{ai_color};
                        box-shadow:
                        0 0 18px {ai_color};
                        border:2px solid white;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-size:12px;
                    ">🤖</div>
                    """

                # Power core
                elif [r, c] in st.session_state.power_cores:

                    content = """
                    <div style="
                        width:14px;
                        height:14px;
                        border-radius:50%;
                        background:#ffe600;
                        box-shadow:
                        0 0 16px #ffe600;
                        animation:pulse 1s infinite;
                    "></div>
                    """

                # Pellet
                elif [r, c] in st.session_state.pellets:

                    content = """
                    <div style="
                        width:6px;
                        height:6px;
                        border-radius:50%;
                        background:#f9a8d4;
                        box-shadow:
                        0 0 7px #f9a8d4;
                    "></div>
                    """

                html += f"""
                <div style="
                    width:28px;
                    height:28px;
                    border-radius:7px;
                    background:rgba(15,23,42,.5);
                    display:flex;
                    align-items:center;
                    justify-content:center;
                ">
                {content}
                </div>
                """

    html += """
    </div>
    </div>

    <style>

    @keyframes pulse {
        0% { transform:scale(.8); }
        50% { transform:scale(1.2); }
        100% { transform:scale(.8); }
    }

    </style>
    """

    return html


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="neuro-title">NEUROCHASE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="neuro-subtitle">'
    'HUMAN INTELLIGENCE × ARTIFICIAL INTELLIGENCE'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# TOP STATS
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    st.markdown(
        f"""
        <div class="stat-box">
        <div class="stat-label">SCORE</div>
        <div class="stat-number" style="color:#ffe600;">
        ⭐ {st.session_state.score}
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    hearts = "❤️" * st.session_state.lives

    st.markdown(
        f"""
        <div class="stat-box">
        <div class="stat-label">LIVES</div>
        <div class="stat-number">
        {hearts if hearts else "💔"}
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        f"""
        <div class="stat-box">
        <div class="stat-label">ROUND</div>
        <div class="stat-number" style="color:#c084fc;">
        {st.session_state.round} / 5
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:

    st.markdown(
        f"""
        <div class="stat-box">
        <div class="stat-label">EXPERIENCE</div>
        <div class="stat-number" style="color:#34d399;">
        🧠 {st.session_state.experience}
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col5:

    accuracy = 0

    if st.session_state.total_predictions > 0:

        accuracy = int(
            (
                st.session_state.correct_predictions /
                st.session_state.total_predictions
            ) * 100
        )

    st.markdown(
        f"""
        <div class="stat-box">
        <div class="stat-label">AI ACCURACY</div>
        <div class="stat-number" style="color:#22d3ee;">
        {accuracy}%
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# GAME MESSAGE
# ============================================================

if st.session_state.game_over:

    st.markdown(
        f"""
        <div class="game-message"
        style="
        border-color:#ff2b6d;
        background:rgba(255,43,109,.12);
        color:#ff7aa2;
        ">
        💀 GAME OVER 💀<br>
        <span style="font-size:14px;">
        The AI learned your movement pattern.
        </span><br>
        <span style="font-size:13px;">
        Final Score: {st.session_state.score}
        </span>
        </div>
        """,
        unsafe_allow_html=True
    )

elif st.session_state.finished:

    st.markdown(
        f"""
        <div class="game-message"
        style="
        border-color:#22c55e;
        background:rgba(34,197,94,.12);
        color:#86efac;
        ">
        🏆 NEUROCHASE MASTER! 🏆<br>
        <span style="font-size:14px;">
        You defeated all 5 rounds of the adaptive AI!
        </span><br>
        <span style="font-size:13px;">
        Final Score: {st.session_state.score}
        </span>
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        f"""
        <div class="game-message">
        {st.session_state.message}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MAIN GAME AREA
# ============================================================

left, right = st.columns([2.5, 1])


# ============================================================
# GAME
# ============================================================

with left:

    st.markdown(
        '<div class="card-title">🕹️ NEON MAZE ARENA</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        draw_maze(),
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="instruction">
        ⬆️ UP &nbsp;&nbsp;
        ⬇️ DOWN &nbsp;&nbsp;
        ⬅️ LEFT &nbsp;&nbsp;
        ➡️ RIGHT
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# AI DASHBOARD
# ============================================================

with right:

    st.markdown(
        '<div class="neuro-card ai-panel">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card-title">🧠 AI BRAIN</div>',
        unsafe_allow_html=True
    )

    prediction = st.session_state.last_prediction

    st.markdown(
        f"""
        <div style="
        font-size:12px;
        color:#94a3b8;
        ">
        PREDICTED NEXT MOVE
        </div>

        <div style="
        font-size:30px;
        font-weight:900;
        color:#22d3ee;
        margin:8px 0 15px;
        ">
        🔮 {prediction}
        </div>
        """,
        unsafe_allow_html=True
    )

    learning_percentage = min(
        100,
        st.session_state.experience
    )

    st.markdown(
        f"""
        <div style="
        font-size:11px;
        color:#94a3b8;
        ">
        LEARNING EXPERIENCE
        </div>

        <div class="learning">
            <div class="learning-fill"
            style="width:{learning_percentage}%;">
            </div>
        </div>

        <div style="
        font-size:11px;
        color:#64748b;
        margin-top:5px;
        ">
        {st.session_state.experience} movement samples recorded
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="font-size:12px;color:#94a3b8;">
        MOVEMENT PATTERN
        </div>

        <div style="
        margin-top:8px;
        line-height:1.9;
        font-size:12px;
        ">

        🔼 UP:
        <b>{st.session_state.learning["UP"]}</b>
        <br>

        🔽 DOWN:
        <b>{st.session_state.learning["DOWN"]}</b>
        <br>

        ◀️ LEFT:
        <b>{st.session_state.learning["LEFT"]}</b>
        <br>

        ▶️ RIGHT:
        <b>{st.session_state.learning["RIGHT"]}</b>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# DIFFICULTY
# ============================================================

st.markdown(
    f"""
    <div class="neuro-card">
    <div class="card-title">⚡ AI DIFFICULTY SYSTEM</div>

    <div style="
    display:flex;
    justify-content:space-between;
    gap:8px;
    flex-wrap:wrap;
    ">

    <div style="
    padding:10px 15px;
    border-radius:10px;
    background:rgba(34,211,238,.10);
    color:#67e8f9;
    ">
    ROUND 1<br>
    <small>LEARNING</small>
    </div>

    <div style="
    padding:10px 15px;
    border-radius:10px;
    background:rgba(59,130,246,.10);
    color:#60a5fa;
    ">
    ROUND 2<br>
    <small>OBSERVING</small>
    </div>

    <div style="
    padding:10px 15px;
    border-radius:10px;
    background:rgba(168,85,247,.10);
    color:#c084fc;
    ">
    ROUND 3<br>
    <small>ADAPTING</small>
    </div>

    <div style="
    padding:10px 15px;
    border-radius:10px;
    background:rgba(236,72,153,.10);
    color:#f472b6;
    ">
    ROUND 4<br>
    <small>PREDICTING</small>
    </div>

    <div style="
    padding:10px 15px;
    border-radius:10px;
    background:rgba(244,63,94,.10);
    color:#fb7185;
    ">
    ROUND 5<br>
    <small>HUNTING</small>
    </div>

    </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CONTROLS
# ============================================================

st.markdown(
    '<div class="card-title">🎮 PLAYER CONTROLS</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:

    if st.button("⬆️ UP", use_container_width=True):
        perform_turn("UP")
        st.rerun()

with c2:

    if st.button("⬅️ LEFT", use_container_width=True):
        perform_turn("LEFT")
        st.rerun()

with c3:

    if st.button("⬇️ DOWN", use_container_width=True):
        perform_turn("DOWN")
        st.rerun()

with c4:

    if st.button("➡️ RIGHT", use_container_width=True):
        perform_turn("RIGHT")
        st.rerun()

with c5:

    if st.button("🔄 RESTART", use_container_width=True):
        initialize_game()
        st.rerun()


# ============================================================
# HOW THE AI WORKS
# ============================================================

st.markdown(
    """
    <div class="neuro-card">

    <div class="card-title">
    🤖 HOW NEUROCHASE LEARNS
    </div>

    <div style="
    color:#cbd5e1;
    font-size:13px;
    line-height:2;
    ">

    <b style="color:#22d3ee;">01.</b>
    The player moves through the maze.

    <br>

    <b style="color:#a78bfa;">02.</b>
    Every movement is recorded by the AI.

    <br>

    <b style="color:#f472b6;">03.</b>
    The AI counts how frequently each direction is used.

    <br>

    <b style="color:#34d399;">04.</b>
    Recent movement patterns receive more importance.

    <br>

    <b style="color:#ffe600;">05.</b>
    The AI predicts the player's next movement.

    <br>

    <b style="color:#fb7185;">06.</b>
    As the rounds increase, the AI relies more heavily
    on its learned prediction.

    <br>

    <b style="color:#c084fc;">07.</b>
    The player must change their strategy to defeat
    the increasingly adaptive AI.

    </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LEGEND
# ============================================================

st.markdown(
    """
    <div class="neuro-card">

    <div class="card-title">
    ✨ LEGEND
    </div>

    <div class="legend">

    🔵 <b>BLUE PLAYER</b> — Human player

    <br>

    🤖 <b>PINK ROBOT</b> — Adaptive AI

    <br>

    🟡 <b>YELLOW CORE</b> — Power-up

    <br>

    🟣 <b>PURPLE WALL</b> — Maze boundary

    <br>

    🩷 <b>PINK DOT</b> — Score pellet

    </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
    text-align:center;
    color:#475569;
    font-size:11px;
    padding:15px;
    letter-spacing:2px;
    ">
    NEUROCHASE • HUMAN INTELLIGENCE VS ARTIFICIAL INTELLIGENCE
    </div>
    """,
    unsafe_allow_html=True
)
