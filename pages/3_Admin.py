from pipeline.extract_data import parse_course_pdf
import streamlit as st
from pipeline.extract_course_data import write_course_to_firestore
from auth import require_auth


require_auth()  # blocks everything below if not logged in

st.title("Admin")

if st.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()


def manual_course_form():
    st.subheader("Add course manually")

    with st.form("manual_course_form"):
        col1, col2 = st.columns(2)
        with col1:
            title       = st.text_input("Title")
            class_id    = st.text_input("Class ID")
            instructor  = st.text_input("Instructor")
            course_type = st.text_input("Course type")
        with col2:
            location    = st.text_input("Location")
            cost        = st.number_input("Cost", min_value=0.0, step=0.01)
            description = st.text_area("Description")

        st.markdown("---")

        # List fields — one value per line
        st.markdown("**Learning objectives** — one per line")
        learning_objectives_raw = st.text_area("", key="lo", height=100)

        st.markdown("**Provided materials** — one per line")
        provided_materials_raw = st.text_area("", key="pm", height=100)

        st.markdown("**Skills** — one per line")
        skills_raw = st.text_area("", key="sk", height=100)

        submitted = st.form_submit_button("Add course")

    if submitted:
        # Parse list fields — split by newline, strip whitespace, drop empty lines
        def parse_list(raw): 
            return [x.strip() for x in raw.strip().splitlines() if x.strip()]

        course = {
            "title":                title.strip(),
            "class_id":             class_id.strip(),
            "instructor":           instructor.strip(),
            "course_type":          course_type.strip(),
            "location":             location.strip(),
            "cost":                 cost,
            "description":          description.strip(),
            "learning_objectives":  parse_list(learning_objectives_raw),
            "provided_materials":   parse_list(provided_materials_raw),
            "skills":               parse_list(skills_raw),
        }

        # Basic validation
        missing = [k for k, v in course.items() if not v and v != 0.0]
        if missing:
            st.warning(f"Missing fields: {', '.join(missing)}")
        else:
            with st.spinner("Writing to database..."):
                write_course_to_firestore(course)
            st.success(f"✅ Course '{title}' added successfully!")



tab1, tab2 = st.tabs(["Upload PDF", "Add manually"])

with tab1:
    uploaded = st.file_uploader("Upload course PDF", type="pdf")
    if uploaded:
        with st.spinner("Extracting and uploading..."):
            course_info = parse_course_pdf(uploaded)
            write_course_to_firestore(course_info)
        st.success(f"Done — {uploaded.name} uploaded")

with tab2:
    manual_course_form()