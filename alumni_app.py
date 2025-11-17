import streamlit as st
from db import (
    init_db,
    get_alumni,
    get_alumni_by_id,
    get_degrees_for_alumni,
    get_employment_for_alumni,
    get_memberships_for_alumni,
    get_contributions_for_alumni,
    get_summary_stats,
)

# Ensure DB and sample data exist
init_db()

st.set_page_config(page_title="Alumni Subsystem", layout="wide")
st.title("Howard University School of Business – Alumni & Student Portal")

st.caption("Demo: A central place where admins track alumni success and students can see alumni profiles.")

page = st.sidebar.selectbox(
    "Navigate",
    ["Dashboard", "Alumni Directory", "Alumni Profile"]
)

# ---------- DASHBOARD ----------
if page == "Dashboard":
    st.header("Dashboard Overview")

    stats = get_summary_stats()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Alumni", stats["total_alumni"])
    col2.metric("Total Employers", stats["total_employers"])
    col3.metric("Active Campaigns", stats["total_campaigns"])
    col4.metric("Total Contributions", f"${stats['total_contributions']:,.2f}")

    st.markdown("""
    **How this supports our project goal:**
    - Admins can quickly see how many alumni are in the system.
    - They can track fundraising campaign performance.
    - They can monitor alumni employment outcomes (success stories).
    """)

# ---------- ALUMNI DIRECTORY ----------
elif page == "Alumni Directory":
    st.header("Alumni Directory")

    alumni_df = get_alumni()

    search = st.text_input("Search by last name or major")

    if search:
        mask = (
            alumni_df["LASTNAME"].str.contains(search, case=False, na=False)
            | alumni_df["GRAD_MAJOR"].str.contains(search, case=False, na=False)
        )
        filtered = alumni_df[mask]
    else:
        filtered = alumni_df

    st.write("Click an AlumniID, then go to **Alumni Profile** to view details.")
    st.dataframe(
        filtered[["ALUMNIID", "FIRSTNAME", "LASTNAME",
                  "PRIMARYEMAIL", "ALUM_GRADYEAR", "GRAD_MAJOR", "MAILING_LIST"]],
        use_container_width=True
    )

# ---------- ALUMNI PROFILE ----------
elif page == "Alumni Profile":
    st.header("Alumni Profile")

    alumni_df = get_alumni().sort_values("ALUMNIID")
    selected_id = st.selectbox(
        "Select an alumni",
        alumni_df["ALUMNIID"],
        format_func=lambda x: f"{x} - {alumni_df[alumni_df['ALUMNIID']==x]['FIRSTNAME'].iloc[0]} "
                              f"{alumni_df[alumni_df['ALUMNIID']==x]['LASTNAME'].iloc[0]}"
    )

    alum = get_alumni_by_id(selected_id).iloc[0]

    st.subheader(f"{alum['FIRSTNAME']} {alum['LASTNAME']}")
    st.write(f"**Email:** {alum['PRIMARYEMAIL']}")
    st.write(f"**Phone:** {alum['PHONE']}")
    st.write(f"**Major:** {alum['GRAD_MAJOR']}")
    st.write(f"**Graduation Year:** {alum['ALUM_GRADYEAR']}")
    st.write(f"**Mailing List Opt-In:** {alum['MAILING_LIST']}")

    st.markdown("This profile shows how admins/students can view alumni success and contact information.")

    tab_deg, tab_emp, tab_mem, tab_contrib = st.tabs(
        ["Degrees", "Employment", "Memberships", "Contributions"]
    )

    with tab_deg:
        st.subheader("Academic Degrees")
        deg_df = get_degrees_for_alumni(selected_id)
        if deg_df.empty:
            st.info("No degree records for this alumni yet.")
        else:
            st.dataframe(deg_df[["MAJOR", "MINOR", "SCHOOL",
                                 "HONORS", "GRADMONTH", "GRADYEAR"]], use_container_width=True)

    with tab_emp:
        st.subheader("Employment History")
        emp_df = get_employment_for_alumni(selected_id)
        if emp_df.empty:
            st.info("No employment records for this alumni yet.")
        else:
            st.dataframe(emp_df, use_container_width=True)
            st.markdown("_This highlights alumni success in the job market._")

    with tab_mem:
        st.subheader("Alumni Association Memberships")
        mem_df = get_memberships_for_alumni(selected_id)
        if mem_df.empty:
            st.info("No memberships on record.")
        else:
            st.dataframe(mem_df, use_container_width=True)

    with tab_contrib:
        st.subheader("Contributions & Giving")
        cont_df = get_contributions_for_alumni(selected_id)
        if cont_df.empty:
            st.info("No contributions on record.")
        else:
            st.dataframe(cont_df, use_container_width=True)
            total = cont_df["AMOUNT"].sum()
            st.write(f"**Total given by this alumni:** ${total:,.2f}")
