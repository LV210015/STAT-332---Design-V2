import streamlit as st
import time
import random
import os
from datetime import datetime
from PIL import Image

# --- CONFIG ---
st.set_page_config(page_title="STAT 332 Survey", layout="centered", initial_sidebar_state="collapsed")

# --- VALID CODES BY GROUP ---
valid_answers = {
    "MCND": ["R5UM", "X4GE", "H2KD", "P7CQ", "6TVA", "D8YR"],
    "MCSD": ["N8QJ", "S4VA", "E9DX", "T3KM", "J5NZ", "V6RC"],
    "MCCD": ["Q2BT", "G7MW", "U8FX", "A9CJ", "M4KP", "X6DN"],
    "NCND": ["A7KQ", "M9TX", "8ZRD", "V3NC", "F6JP", "2WBY"],
    "NCSD": ["K3BN", "Z9MU", "B5FX", "Y2GW", "C6TR", "W7HP"],
    "NCCD": ["F3YV", "B7QA", "Z5HW", "H6GT", "R2NX", "Y8PC"]
}

# --- SESSION STATE INIT ---
if "step" not in st.session_state:
    st.session_state.step = "start"
if "username" not in st.session_state:
    st.session_state.username = ""
if "images" not in st.session_state:
    st.session_state.images = []
if "results" not in st.session_state:
    st.session_state.results = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = 0
if "image_dir" not in st.session_state:
    st.session_state.image_dir = "images"

# --- RANDOMIZE IMAGES ---
def load_images():
    images = []
    for group in valid_answers.keys():
        selected = random.sample(range(1, 7), 2)
        for i in selected:
            filename = f"{group}{i}.jpg"
            images.append((group, filename))
    random.shuffle(images)
    return images

# --- START PAGE ---
def show_start():
    st.title("STAT 332 Experiment")
    st.subheader("The Impact of Color & Distortion on Code Recognition")
    name = st.text_input("Enter your nickname to begin:", key="name")
    if st.button("Start Survey"):
        if name.strip() == "":
            st.warning("Please enter a valid nickname.")
        else:
            st.session_state.username = name.strip()
            st.session_state.images = load_images()
            st.session_state.step = "instructions"
            st.experimental_rerun()

# --- INSTRUCTIONS ---
def show_instructions():
    st.header("Instructions")
    st.markdown("""
    1. You will see **12 images** of verification codes.
    2. For each image, click **'I Recognized It!'** once you see the code.
    3. A text box will appear. Please enter the code you saw.
    4. Don't worry — there are no confusing characters like '0' or 'O'.
    5. Please type carefully. Each entry helps our research.
    """)
    if st.button("Begin Survey"):
        st.session_state.step = "survey"
        st.experimental_rerun()

# --- SURVEY PAGE ---
def show_survey():
    index = st.session_state.current_index
    if index >= 12:
        st.session_state.step = "end"
        st.experimental_rerun()
    group, filename = st.session_state.images[index]
    st.subheader(f"Trial {index + 1} — Group: {group}")

    image_path = os.path.join(st.session_state.image_dir, filename)
    st.image(Image.open(image_path), width=300)

    if "clicked" not in st.session_state:
        st.session_state.clicked = False

    if not st.session_state.clicked:
        if st.button("I Recognized It!"):
            st.session_state.start_time = time.time()
            st.session_state.clicked = True
            st.experimental_rerun()
    else:
        answer = st.text_input("Enter the code you saw:", key=f"answer_{index}")
        if st.button("Submit"):
            end_time = time.time()
            elapsed = round(end_time - st.session_state.start_time, 3)
            cleaned = answer.strip().upper()
            is_correct = cleaned in valid_answers[group]

            st.session_state.results.append({
                "Username": st.session_state.username,
                "Trial": index + 1,
                "Color": "Mixed" if group.startswith("MC") else "No Color",
                "Distortion": "None" if group.endswith("ND") else ("Simple" if group.endswith("SD") else "Complex"),
                "Time_sec": elapsed,
                "Answer": cleaned,
                "Timestamp": datetime.now().isoformat(),
                "Correct": is_correct
            })

            st.session_state.current_index += 1
            st.session_state.clicked = False
            st.experimental_rerun()

# --- END PAGE ---
def show_end():
    st.success("✅ Survey Completed. Thank you!")
    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df)
    st.download_button("Download CSV", data=df.to_csv(index=False), file_name="results.csv")

# --- ROUTING ---
if st.session_state.step == "start":
    show_start()
elif st.session_state.step == "instructions":
    show_instructions()
elif st.session_state.step == "survey":
    show_survey()
elif st.session_state.step == "end":
    show_end()
