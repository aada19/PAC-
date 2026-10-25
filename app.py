import streamlit as st
import random
import math

# ============================================================
# NEUROCHASE
# Human Intelligence vs Artificial Intelligence
# Streamlit Edition
# ============================================================

st.set_page_config(
    page_title="NEUROCHASE - Adaptive AI Game",
    page_icon="🧠",
    layout="wide"
)

# ============================================================
# COLORS / CONSTANTS
# ============================================================

ROWS = 19
COLS = 24

# ============================================================
# MAZE
# ============================================================

MAZE = [
    "########################",
    "#P     #       #       #",
    "# ###  # ##### # ##### #",
    "#      #     # #       #",
    "###### ##### # ######  #",
    "#          #            #",
    "# ######## # #########  #",
    "#        #              #",
    "# ###### ########### ## #",
    "#      #        #       #",
    "#####  # ###### # ##### #",
    "#      #      # #       #",
    "# ####### ### # ####### #",
    "#         #   #         #",
    "# ####### # ####### ### #",
    "#       #       #       #",
    "# ### # ####### # ##### #",
    "#     #         #       #",
    "########################"
]

# ============================================================
# FIND PLAYER START
# ============================================================

player_start = None

for row in range(len(MAZE)):
    for col in range(len(MAZE[row])):
        if MAZE[row][col] == "P":
            player_start = (row, col)

# ============================================================
# SESSION STATE
# ============================================================

if "player" not in st.session_state:
    st.session_state.player = player_start

if "enemy" not in st.session_state:
    st.session_state.enemy = (17, 21)

if "moves" not in st.session_state:
    st.session_state.moves = {
        "UP": 0,
        "DOWN": 0,
        "LEFT": 0,
        "RIGHT": 0
    }

if "patterns" not in st.session_state:
    st.session_state.patterns = {}

if "experience" not in st.session_state:
    st.session_state.experience = 0

if "prediction" not in st.session_state:
    st.session_state.prediction = "UNKNOWN"

if "correct_predictions" not in st.session_state:
    st.session_state.correct_predictions = 0

if "prediction_attempts" not in st.session_state:
    st.session_state.prediction_attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "lives" not in st.session_state:
    st.session_state.lives = 3

if "last_direction" not in st.session_state:
    st.session_state.last_direction = None

if "game_over" not in st.session_state:
    st.session_state.game_over = False


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_wall(row, col):
    """Check whether a maze position is a wall."""

    if row < 0 or row >= ROWS:
        return True

    if col < 0 or col >= COLS:
        return True

    return MAZE[row][col] == "#"


def move_player(direction):
    """Move player and teach AI."""

    row, col = st.session_state.player

    new_row = row
    new_col = col

    if direction == "UP":
        new_row -= 1

    elif direction == "DOWN":
        new_row += 1

    elif direction == "LEFT":
        new_col -= 1

    elif direction == "RIGHT":
        new_col += 1

    # Don't move through walls
    if not is_wall(new_row, new_col):

        st.session_state.player = (new_row, new_col)

        # Learn player behaviour
        learn_from_player(direction)

        # Move AI
        update_ai()

        # Check collision
        check_collision()


# ============================================================
# AI LEARNING
# ============================================================

def get_situation():

    player_row, player_col = st.session_state.player
    enemy_row, enemy_col = st.session_state.enemy

    dx = player_col - enemy_col
    dy = player_row - enemy_row

    horizontal = "RIGHT" if dx > 0 else "LEFT"
    vertical = "DOWN" if dy > 0 else "UP"

    distance = math.sqrt(dx * dx + dy * dy)

    if distance < 4:
        danger = "CLOSE"

    elif distance < 8:
        danger = "MEDIUM"

    else:
        danger = "FAR"

    return (
        horizontal,
        vertical,
        danger
    )


def learn_from_player(direction):

    situation = get_situation()

    # General movement learning
    st.session_state.moves[direction] += 1

    # Situation-specific learning
    if situation not in st.session_state.patterns:

        st.session_state.patterns[situation] = {
            "UP": 0,
            "DOWN": 0,
            "LEFT": 0,
            "RIGHT": 0
        }

    st.session_state.patterns[situation][direction] += 1

    st.session_state.experience += 1

    # Check previous prediction
    previous_prediction = st.session_state.prediction

    if previous_prediction != "UNKNOWN":

        st.session_state.prediction_attempts += 1

        if previous_prediction == direction:

            st.session_state.correct_predictions += 1


# ============================================================
# AI PREDICTION
# ============================================================

def predict_player():

    situation = get_situation()

    patterns = st.session_state.patterns

    if situation not in patterns:

        prediction = random.choice([
            "UP",
            "DOWN",
            "LEFT",
            "RIGHT"
        ])

    else:

        data = patterns[situation]

        prediction = max(
            data,
            key=data.get
        )

        if data[prediction] == 0:

            prediction = random.choice([
                "UP",
                "DOWN",
                "LEFT",
                "RIGHT"
            ])

    st.session_state.prediction = prediction

    return prediction


# ============================================================
# AI MOVEMENT
# ============================================================

def update_ai():

    prediction = predict_player()

    player_row, player_col = st.session_state.player
    enemy_row, enemy_col = st.session_state.enemy

    target_row = player_row
    target_col = player_col

    prediction_distance = 2

    if prediction == "UP":
        target_row -= prediction_distance

    elif prediction == "DOWN":
        target_row += prediction_distance

    elif prediction == "LEFT":
        target_col -= prediction_distance

    elif prediction == "RIGHT":
        target_col += prediction_distance

    # Try to move towards predicted position
    possible_moves = []

    if target_row < enemy_row:
        possible_moves.append(("UP", -1, 0))

    if target_row > enemy_row:
        possible_moves.append(("DOWN", 1, 0))

    if target_col < enemy_col:
        possible_moves.append(("LEFT", 0, -1))

    if target_col > enemy_col:
        possible_moves.append(("RIGHT", 0, 1))

    # Add alternative moves
    possible_moves.extend([
        ("UP", -1, 0),
        ("DOWN", 1, 0),
        ("LEFT", 0, -1),
        ("RIGHT", 0, 1)
    ])

    for _, dr, dc in possible_moves:

        new_row = enemy_row + dr
        new_col = enemy_col + dc

        if not is_wall(new_row, new_col):

            st.session_state.enemy = (
                new_row,
                new_col
            )

            break


# ============================================================
# COLLISION
# ============================================================

def check_collision():

    player = st.session_state.player
    enemy = st.session_state.enemy

    distance = math.sqrt(
        (player[0] - enemy[0]) ** 2 +
        (player[1] - enemy[1]) ** 2
    )

    if distance <= 1.0:

        st.session_state.lives -= 1

        if st.session_state.lives <= 0:

            st.session_state.game_over = True

        else:

            st.session_state.player = player_start

            st.session_state.enemy = (17, 21)


# ============================================================
# RESET
# ============================================================

def restart_game():

    st.session_state.player = player_start

    st.session_state.enemy = (17, 21)

    st.session_state.moves = {
        "UP": 0,
        "DOWN": 0,
        "LEFT": 0,
        "RIGHT": 0
    }

    st.session_state.patterns = {}

    st.session_state.experience = 0

    st.session_state.prediction = "UNKNOWN"

    st.session_state.correct_predictions = 0

    st.session_state.prediction_attempts = 0

    st.session_state.score = 0

    st.session_state.lives = 3

    st.session_state.last_direction = None

    st.session_state.game_over = False


# ============================================================
# AI STATISTICS
# ============================================================

def confidence():

    total = sum(
        st.session_state.moves.values()
    )

    if total == 0:
        return 0

    largest = max(
        st.session_state.moves.values()
    )

    return int(
        largest / total * 100
    )


def accuracy():

    attempts = st.session_state.prediction_attempts

    if attempts == 0:
        return 0

    return int(
        st.session_state.correct_predictions
        / attempts
        * 100
    )


def most_common_move():

    if st.session_state.experience == 0:
        return "UNKNOWN"

    return max(
        st.session_state.moves,
        key=st.session_state.moves.get
    )


def ai_status():

    experience = st.session_state.experience

    if experience > 120:
        return "PREDICTING"

    elif experience > 50:
        return "ADAPTING"

    else:
        return "LEARNING"


# ============================================================
# MAZE DISPLAY
# ============================================================

def create_maze_html():

    player_row, player_col = st.session_state.player
    enemy_row, enemy_col = st.session_state.enemy

    html = """
    <div class="maze">
    """

    for row in range(ROWS):

        for col in range(COLS):

            if row == player_row and col == player_col:

                html += '<div class="cell player">🧠</div>'

            elif row == enemy_row and col == enemy_col:

                html += '<div class="cell enemy">🤖</div>'

            elif MAZE[row][col] == "#":

                html += '<div class="cell wall"></div>'

            else:

                html += '<div class="cell path"></div>'

    html += "</div>"

    return html


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0c121e;
        color: #f0f5fa;
    }

    .title {
        font-size: 42px;
        font-weight: bold;
        color: #32dc96;
        text-align: center;
        margin-bottom: 0px;
    }

    .subtitle {
        text-align: center;
        color: #9aa6b5;
        margin-bottom: 20px;
    }

    .maze {

        display: grid;

        grid-template-columns:
        repeat(24, 25px);

        grid-template-rows:
        repeat(19, 25px);

        gap: 1px;

        background: #05080f;

        padding: 10px;

        border-radius: 10px;

        width: fit-content;

        margin: auto;

    }

    .cell {

        width: 25px;
        height: 25px;

        display: flex;

        align-items: center;
        justify-content: center;

        font-size: 17px;

    }

    .wall {

        background: #2d3c50;

        border: 1px solid #41556e;

    }

    .path {

        background: #111b2b;

    }

    .player {

        background: #3ca0ff;

        border-radius: 50%;

    }

    .enemy {

        background: #f0465a;

        border-radius: 50%;

    }

    .metric-card {

        background: #141c2d;

        padding: 15px;

        border-radius: 10px;

        border: 1px solid #29364c;

        margin-bottom: 10px;

    }

    .metric-title {

        color: #9aa6b5;

        font-size: 13px;

    }

    .metric-value {

        font-size: 25px;

        font-weight: bold;

        color: #32dc96;

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="title">🧠 NEUROCHASE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Human Intelligence vs Artificial Intelligence'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# GAME / AI PANEL
# ============================================================

game_col, panel_col = st.columns(
    [2.2, 1]
)


# ============================================================
# GAME
# ============================================================

with game_col:

    st.markdown("### 🌀 Adaptive AI Maze")

    st.markdown(
        create_maze_html(),
        unsafe_allow_html=True
    )

    st.write("")

    # Controls

    col1, col2, col3 = st.columns(3)

    with col2:

        if st.button("⬆️", use_container_width=True):

            if not st.session_state.game_over:

                move_player("UP")

                st.rerun()

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button("⬅️", use_container_width=True):

            if not st.session_state.game_over:

                move_player("LEFT")

                st.rerun()

    with col2:

        if st.button("⬇️", use_container_width=True):

            if not st.session_state.game_over:

                move_player("DOWN")

                st.rerun()

    with col3:

        if st.button("➡️", use_container_width=True):

            if not st.session_state.game_over:

                move_player("RIGHT")

                st.rerun()

    st.caption(
        "Use the buttons to move. "
        "The AI observes your behaviour and learns your patterns."
    )


# ============================================================
# AI PANEL
# ============================================================

with panel_col:

    st.markdown("## 🧠 AI BRAIN")

    st.metric(
        "Experience",
        st.session_state.experience
    )

    st.metric(
        "AI Confidence",
        f"{confidence()}%"
    )

    st.metric(
        "Prediction",
        st.session_state.prediction
    )

    st.metric(
        "Prediction Accuracy",
        f"{accuracy()}%"
    )

    st.metric(
        "Most Common Move",
        most_common_move()
    )

    st.divider()

    st.markdown("### PLAYER BEHAVIOUR")

    total = sum(
        st.session_state.moves.values()
    )

    for direction in [
        "UP",
        "DOWN",
        "LEFT",
        "RIGHT"
    ]:

        count = st.session_state.moves[direction]

        if total > 0:

            percentage = int(
                count / total * 100
            )

        else:

            percentage = 0

        st.write(
            f"**{direction}** — {percentage}%"
        )

        st.progress(
            percentage / 100
        )

    st.divider()

    st.write(
        f"**STATUS:** {ai_status()}"
    )

    st.write(
        f"**SCORE:** {st.session_state.score}"
    )

    st.write(
        f"**LIVES:** {st.session_state.lives}"
    )

    if st.button(
        "🔄 RESTART GAME",
        use_container_width=True
    ):

        restart_game()

        st.rerun()


# ============================================================
# GAME OVER
# ============================================================

if st.session_state.game_over:

    st.error(
        "🤖 AI HAS LEARNED YOUR MOVEMENT!"
    )

    st.warning(
        "Restart the game and try a different strategy."
    )


# ============================================================
# EXPLANATION
# ============================================================

st.divider()

st.markdown("## 🔬 How the AI Works")

info1, info2, info3 = st.columns(3)

with info1:

    st.markdown(
        """
        ### 👀 1. Observe

        The AI observes the player's
        movement direction and the
        player's distance from the AI.
        """
    )

with info2:

    st.markdown(
        """
        ### 🧠 2. Learn

        The AI records movement patterns
        and builds experience from every
        player action.
        """
    )

with info3:

    st.markdown(
        """
        ### 🎯 3. Predict

        The AI uses learned behaviour
        to predict the player's next
        movement.
        """
    )

st.caption(
    "NEUROCHASE • Human Intelligence vs Artificial Intelligence"
)
