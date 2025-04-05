import streamlit as st
import os
import random
import time
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="STAT 332 Survey", layout="centered", initial_sidebar_state="collapsed")
# ---- Group Prefixes and Valid Codes ----
group_prefixes = {
    "MCND": "Mixed Color + No Distortion",
    "MCSD": "Mixed Color + Simple Distortion",
    "MCCD": "Mixed Color + Complex Distortion",
    "NCND": "No Color + No Distortion",
    "NCSD": "No Color + Simple Distortion",
    "NCCD": "No Color + Complex Distortion"
}

valid_answers = {
    "MCND": ["R5UM", "X4GE", "H2KD", "P7CQ", "6TVA", "D8YR"],
    "MCSD": ["N8QJ", "S4VA", "E9DX", "T3KM", "J5NZ", "V6RC"],
    "MCCD": ["Q2BT", "G7MW", "U8FX", "A9CJ", "M4KP", "X6DN"],
    "NCND": ["A7KQ", "M9TX", "8ZRD", "V3NC", "F6JP", "2WBY"],
    "NCSD": ["K3BN", "Z9MU", "B5FX", "Y2GW", "C6TR", "W7HP"],
    "NCCD": ["F3YV", "B7QA", "Z5HW", "H6GT", "R2NX", "Y8PC"]
}

# ---- Load 2 Random Images from Each Group ----
def load_images():
    images_dir = "images"
    all_selected = []
    for prefix in group_prefixes:
        group_images = [f for f in os.listdir(images_dir) if f.startswith(prefix) and f.endswith(".jpg")]
        selected = random.sample(group_images, 2)
        for img in selected:
            all_selected.append({
                "filename": img,
                "group": prefix,
                "label": group_prefixes[prefix]
            })
    random.shuffle(all_selected)
    return all_selected

# ---- Streamlit Session State Setup ----
st.set_page_config(page_title="STAT 332 Survey", layout="centered")

if "step" not in st.session_state:
    st.session_state.step = "start"
if "name" not in st.session_state:
    st.session_state.name = ""
if "images" not in st.session_state:
    st.session_state.images = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "response_time" not in st.session_state:
    st.session_state.response_time = 0
if "answer_ready" not in st.session_state:
    st.session_state.answer_ready = False
if "responses" not in st.session_state:
    st.session_state.responses = []

# ---- Start Page ----
if st.session_state.step == "start":
    st.title("STAT 332 Survey")
    st.subheader("The Impact of Color & Distortion on Code Recognition")
    st.write("Please enter your nickname to begin:")
    name = st.text_input("Nickname")

    if st.button("Start Survey"):
        if name.strip() == "":
            st.warning("Please enter a valid nickname.")
        else:
            st.session_state.name = name.strip()
            st.session_state.step = "instructions"
            st.experimental_rerun()

# ---- Instruction Page ----
elif st.session_state.step == "instructions":
    st.title("Instructions")
    st.markdown("""
1. You’ll see **12 images** of verification codes (2 from each group).
2. For each image, click **"I Recognized It!"** once you recognize the code.
3. After that, a textbox will appear — type what you saw.
4. **Don't worry** — there are no confusing letters like 0 (zero) or O (letter O).
5. All answers are **4 characters long**. Be as accurate as you can.
    """)
    if st.button("Begin Now"):
        st.session_state.images = load_images()
        st.session_state.step = "survey"
        st.experimental_rerun()

# ---- Survey Page ----
elif st.session_state.step == "survey":
    total = len(st.session_state.images)
    i = st.session_state.index
    current = st.session_state.images[i]

    st.subheader(f"Trial {i + 1} of {total}")
    st.text(current["label"])
    st.image(os.path.join("images", current["filename"]), width=300)

    if not st.session_state.answer_ready:
        if st.button("I Recognized It"):
            st.session_state.start_time = time.time()
            st.session_state.answer_ready = True
            st.experimental_rerun()
    else:
        answer = st.text_input("Enter what you saw:")
        if st.button("Submit"):
            end_time = time.time()
            duration = round(end_time - st.session_state.start_time, 3)

            correct_list = valid_answers[current["group"]]
            is_correct = any(answer.strip().upper() == valid.strip().upper() for valid in correct_list)

            st.session_state.responses.append({
                "Username": st.session_state.name,
                "Trial": i + 1,
                "Color": "Mixed" if current["group"].startswith("M") else "Single",
                "Distortion": current["label"].split(", ")[-1],
                "Time_sec": duration,
                "Answer": answer.strip(),
                "Timestamp": datetime.now().isoformat(),
                "Correct": is_correct
            })

            # Advance
            st.session_state.index += 1
            st.session_state.start_time = None
            st.session_state.answer_ready = False

            if st.session_state.index >= total:
                st.session_state.step = "done"
            st.experimental_rerun()

# ---- Final Page ----
elif st.session_state.step == "done":
    st.success("✅ Survey Completed")
    df = pd.DataFrame(st.session_state.responses)
    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Your Results", csv, "survey_results.csv", "text/csv")
