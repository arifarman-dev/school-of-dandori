from pipeline.extract_data import parse_course_pdf
import streamlit as st
from pipeline.extract_course_data import write_course_to_firestore, update_course_in_firestore
from auth import require_auth
from pipeline.fetch_from_firestore import get_all_courses_from_firestore

require_auth()  # blocks everything below if not logged in

st.title("Admin")

if st.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()


def manual_course_form(prefill = None, form_key = "manual_course_form"):
    """
    Reusable course form. Pass `prefill` to pre-populate fields for editing.
    Returns the submitted course dict, or None if not submitted.
    """
    is_edit = prefill is not None
    prefill = prefill or {}

    with st.form(form_key):
        col1, col2 = st.columns(2)
        with col1:
            title       = st.text_input("Title",       value=prefill.get("title", ""))
            class_id    = st.text_input("Class ID",    value=prefill.get("class_id", ""), disabled=is_edit)
            instructor  = st.text_input("Instructor",  value=prefill.get("instructor", ""))
            course_type = st.text_input("Course type", value=prefill.get("course_type", ""))
        with col2:
            location    = st.text_input("Location",    value=prefill.get("location", ""))
            cost        = st.number_input("Cost", min_value=0.0, step=0.01, value=float(prefill.get("cost", 0.0)))
            description = st.text_area("Description",  value=prefill.get("description", ""))

        st.markdown("---")

        def list_to_text(val):
            return "\n".join(val) if isinstance(val, list) else (val or "")

        st.markdown("**Learning objectives** — one per line")
        learning_objectives_raw = st.text_area("", key=f"{form_key}_lo", height=100,
                                                value=list_to_text(prefill.get("learning_objectives", "")))

        st.markdown("**Provided materials** — one per line")
        provided_materials_raw = st.text_area("", key=f"{form_key}_pm", height=100,
                                               value=list_to_text(prefill.get("provided_materials", "")))

        st.markdown("**Skills** — one per line")
        skills_raw = st.text_area("", key=f"{form_key}_sk", height=100,
                                   value=list_to_text(prefill.get("skills", "")))

        label = "Save changes" if is_edit else "Add course"
        submitted = st.form_submit_button(label)

    if submitted:
        def parse_list(raw):
            return [x.strip() for x in raw.strip().splitlines() if x.strip()]

        course = {
            "title":               title.strip(),
            "class_id":            class_id.strip() if not is_edit else prefill["class_id"],
            "instructor":          instructor.strip(),
            "course_type":         course_type.strip(),
            "location":            location.strip(),
            "cost":                cost,
            "description":         description.strip(),
            "learning_objectives": parse_list(learning_objectives_raw),
            "provided_materials":  parse_list(provided_materials_raw),
            "skills":              parse_list(skills_raw),
        }

        missing = [k for k, v in course.items() if not v and v != 0.0]
        if missing:
            st.warning(f"Missing fields: {', '.join(missing)}")
            return None

        return course

    return None

def view_and_edit_courses():
    st.subheader("All courses")
    col1, col2 = st.columns([3, 1])
    with col1:
        pass
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            get_all_courses_from_firestore()
    with st.spinner("Loading courses..."):
        df = get_all_courses_from_firestore()

    if df.empty:
        st.info("No courses found in Firestore.")
        return

    # Summary table — just the key columns for scanning
    display_cols = [c for c in ["class_id", "title", "instructor", "course_type", "location", "cost"] if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True)

    st.markdown("---")
    st.subheader("Edit a course")

    # Select by a readable label
    df["_label"] = df["class_id"] + " — " + df["title"]
    selected_label = st.selectbox("Select course to edit", df["_label"])

    selected_row = df[df["_label"] == selected_label].iloc[0].to_dict()

    original_class_id = selected_row["class_id"]
    original_title = selected_row["title"]

    selected_row.pop("_label", None)
    selected_row.pop("id", None)
    selected_row.pop("updated_at", None)

    updated_course = manual_course_form(prefill=selected_row, form_key="edit_course_form")

    if updated_course:
        with st.spinner("Saving changes..."):
            update_course_in_firestore(original_class_id, original_title, updated_course)
        st.success(f"✅ '{updated_course['title']}' updated successfully!")

tab1, tab2, tab3 = st.tabs(["📤 Upload PDF", "✏️ Add manually", "🗂️ View & Edit"])


with tab1:
    uploaded = st.file_uploader("Upload course PDF", type="pdf")
    if uploaded:
        with st.spinner("Extracting and uploading..."):
            course_info = parse_course_pdf(uploaded)
            write_course_to_firestore(course_info)
        st.success(f"Done — {uploaded.name} uploaded")

with tab2:
    st.subheader("Add course manually")
    course = manual_course_form()
    if course:
        with st.spinner("Writing to database..."):
            write_course_to_firestore(course)
        st.success(f"✅ Course '{course['title']}' added successfully!")

with tab3:
    view_and_edit_courses()