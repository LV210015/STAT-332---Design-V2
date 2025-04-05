import streamlit as st
import random
import os
import pandas as pd
import time
import requests
from datetime import datetime

# --- Google Apps Script Webhook URL ---
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyG6BpxW0MOGPTtkR6-K-rCDHvPZjj7yJvV1Bo2MzvCuVqkQ3tHydPIdyAKmknxPjLXMw/exec"

# --- Image Groups ---
image_folder = "images"
groups = {
    "MCCD": [f"MCCD{i}.jpg" for i in range(1, 7)],
    "MCND": [f"MCND{i}.jpg" for i in range(1, 7)],
    "MLCD": [f"MLCD{i}.jpg" for i in range(1, 7)],
    "MLND": [f"MLND{i}.jpg" for i in range(1, 7)],
    "MPCD": [f"MPCD{i}.jpg" for i in range(1, 7)],
    "MPND": [f"MPND{i}.jpg" for i in range(1, 7)],
}

valid_codes = {key: [img.replace(".jpg", "") for img in val] for key, val in groups.items()}

st.title("The Impact of Color & Distortion on Code Recognition")

# --- Page Navigation ---
if "page" not in st.session_state:
    st.session_state.page = "start"
if "questions" not in st.session_state:
    st.session_state.questions = []
    for group, imgs in groups.items():
        st.session_state.questions.extend([{"group": group, "image": img} for img in random.sample(imgs, 2)])
    random.shuffle(st.session_state.questions)
    st.session_state.answers = []
    st.session_state.trial_start_time = None

# --- Start Page ---
if st.session_state.page == "start":
    st.markdown("""
    ### Welcome to the Visual Recognition Experiment
    
    In this experiment, you will be shown a series of images containing distorted or colored alphanumeric codes.
    Your task is to recognize the code in each image and enter it into the input box provided.

    **Instructions:**
    - You will go through 12 images in total.
    - Each image will appear only once.
    - Enter the exact code you see (e.g., `MCCD4`, not lowercase).
    - Your response time and accuracy will be recorded.

    Please type your nickname below and press **Start Survey** to begin.
    """)
    nickname = st.text_input("Please enter a nickname or username to begin:", key="nickname")
    if st.button("Start Survey") and nickname:
        st.session_state.page = "survey"
        st.experimental_rerun()

# --- Survey Page ---
if st.session_state.page == "survey":
    current_trial = len(st.session_state.answers)

    if current_trial < len(st.session_state.questions):
        q = st.session_state.questions[current_trial]
        img_path = os.path.join(image_folder, q["image"])
        st.image(img_path, caption="Please enter the code you see.")

        if st.session_state.trial_start_time is None:
            st.session_state.trial_start_time = time.time()

        answer = st.text_input("Code:", key=f"response_{current_trial}")

        if st.button("Submit"):
            elapsed = time.time() - st.session_state.trial_start_time
            correct = answer.strip().upper() in [code.upper() for code in valid_codes[q["group"]]]

            result = {
                "Username": st.session_state.get("nickname", ""),
                "Trial": current_trial + 1,
                "Color": q["group"][1],
                "Distortion": q["group"][2],
                "Time_sec": round(elapsed, 3),
                "Answer": answer.strip(),
                "Timestamp": datetime.now().isoformat(),
                "Correct": "TRUE" if correct else "FALSE"
            }

            try:
                requests.post(WEBHOOK_URL, json=result)
            except:
                st.error("Failed to send data to Google Sheet. Check your connection or webhook URL.")

            st.session_state.answers.append(result)
            st.session_state.trial_start_time = None
            st.experimental_rerun()

    else:
        st.write("Thank you for participating. Your responses have been recorded.")
        df = pd.DataFrame(st.session_state.answers)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download My Results (CSV)", csv, "results.csv", "text/csv")
        st.session_state.page = "done"
