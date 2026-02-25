import streamlit as st
from pipeline import generate_learning_path_for_user

st.set_page_config(page_title="AI Learning Path Generator")

st.title("🎓 AI Learning Path Generator")

st.write(
    "Click the button below to generate a personalized learning path "
)

if st.button("🚀 Generate Learning Path"):
    with st.spinner("Generating learning path..."):
        try:
            result = generate_learning_path_for_user(user_id=None)

            st.success("Learning path generated successfully!")

            # ---------- EXTRACT SKILLS FROM PHASES ----------
            phases = result.get("phases", [])

            all_skills = []
            for phase in phases:
                all_skills.extend(phase.get("skills", []))

            # remove duplicates while preserving order
            all_skills = list(dict.fromkeys(all_skills))

            # ---------- DISPLAY ----------
            st.subheader("📌 Recommended Skills")
            for i, skill in enumerate(all_skills, start=1):
                st.write(f"{i}. {skill}")

            st.subheader("🧩 Learning Phases")
            for phase in phases:
                with st.expander(phase["phase"]):
                    st.write("**Skills:**")
                    for s in phase["skills"]:
                        st.write(f"- {s}")
                    st.write(f"**Duration:** {phase['duration_weeks']} weeks")

            st.subheader("🗓 Estimated Duration")
            st.write(f"{result['estimated_duration_weeks']} weeks")

            st.subheader("🎯 Success Probability")
            st.progress(float(result["success_probability"]))

            st.subheader("🧠 Why this learning path?")
            st.write(result["explanation"])

        except Exception as e:
            st.error(str(e))
