import streamlit as st
import time
import random
import pandas as pd
import requests
from datetime import datetime

# Your Google Sheets Webhook URL
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxr9VbH4_pjofYGmTNREOsFYo9J6BEXSFAd5-zkdYVFDHAp-ozKaSuTlb5jEbvt-lvJOg/exec"

# Define valid answers per group
valid_answers = {
    "MCND": ["R5UM", "X4GE", "H2KD", "P7CQ", "6TVA", "D8YR"],
    "MCSD": ["N8QJ", "S4VA", "E9DX", "T3KM", "J5NZ", "V6RC"],
    "MCCD": ["Q2BT", "G7MW", "U8FX", "A9CJ", "M4KP", "X6DN"],
    "NCND": ["A7KQ", "M9TX", "8ZRD", "V3NC", "F6JP", "2WBY"],
    "NCSD": ["K3BN", "Z9MU", "B5FX", "Y2GW", "C6TR", "W7HP"],
    "NCCD": ["F3YV", "B7QA", "Z5HW", "H6GT", "R2NX", "Y8PC"]
}

# Generate randomized trials (2 from each group)
def load_trials():
    trials = []
    for prefix in valid_answers:
        selected = random.sample(valid_answers[prefix], 2)
        for code in selected:
            color = "Mixed" if prefix.startswith("MC") else "Single"
            if "ND" in prefix:
                distortion = "None"
            elif "SD" in prefix:
                distortion = "Simple"
            else:
                distortion = "Complex"
            trials.append({
                "Group": prefix,
                "Color": color,
                "Distortion": distortion,
                "Code": code
            })
    random.shuffle(trials)
    return trials

# UI begins
st.title("Visual Recognition Survey")

# Session state setup
if "trial_index" not in st.session_state:
    st.session_state.trial_index = 0
    st.session_state.trials = load_trials()
    st.session_state.start_time = None
    st.session_state.results = []
    st.session_state.show_input = False
    st.session_state.response_time = None

# Run trials
if st.session_state.trial_index < len(st.session_state.trials):
    trial = st.session_state.trials[st.session_state.trial_index]
    st.subheader(f"Trial {st.session_state.trial_index + 1}")
    st.markdown(f"**Group:** {trial['Group']}  \n**Color:** {trial['Color']}  \n**Distortion:** {trial['Distortion']}")

    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    if st.button("I recognized it"):
        st.session_state.response_time = time.time() - st.session_state.start_time
        st.session_state.show_input = True

    if st.session_state.show_input:
        answer = st.text_input("Enter the code you saw:")
        if st.button("Submit"):
            correct_codes = valid_answers[trial["Group"]]
            is_correct = answer.strip().upper() in [x.upper() for x in correct_codes]

            result = {
                "Trial": st.session_state.trial_index + 1,
                "Color": trial["Color"],
                "Distortion": trial["Distortion"],
                "Time_sec": round(st.session_state.response_time, 3),
                "Answer": answer.strip(),
                "Timestamp": datetime.now().isoformat(),
                "Correct": is_correct
            }

            st.session_state.results.append(result)

            try:
                requests.post(WEBHOOK_URL, json=result)
                if is_correct:
                    st.success("✅ Correct code.")
                else:
                    st.error("❌ Not matched to the expected group.")
            except Exception as e:
                st.warning(f"⚠️ Failed to upload: {e}")

            st.session_state.trial_index += 1
            st.session_state.start_time = None
            st.session_state.show_input = False
            st.session_state.response_time = None
            st.rerun()

else:
    st.success("✅ Survey Completed")
    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Results", csv, "results.csv", "text/csv")
