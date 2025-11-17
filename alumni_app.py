import streamlit as st
import datetime
import pandas as pd

from db import (
    init_db,
    get_alumni,
    get_alumni_by_id,
    get_degrees_for_alumni,
    get_employment_for_alumni,
    get_memberships_for_alumni,
    get_contributions_for_alumni,
    get_summary_stats,
    get_campaigns,
    create_contribution,
    update_alumni_contact,
)

# ---- DEMO USERS ----
VALID_USERS = {
    "admin": {
        "password": "HUSB2024!",
        "role": "Admin",
    },
    "mily.lopez@bison.howard.edu": {
        "password": "001234567",
        "role": "Student",
    },
    # Example alumni user mapped to ALUMNIID 1001 (Maya Johnson)
    "maya.johnson@email.com": {
        "password": "Maya2024!",
        "role": "Alumni",
        "alumni_id": 1001,
    },
}

# Ensure DB and sample data exist
init_db()

st.set_page_config(page_title="Alumni Subsystem", layout="wide")


# ---------- REUSABLE PROFILE RENDERING ----------
def render_alumni_profile(alumni_id: int):
    """Reusable profile view for any alumni_id."""
    alum_df = get_alumni_by_id(alumni_id)
    if alum_df.empty:
        st.error("Alumni not found.")
        return

    alum = alum_df.iloc[0]

    st.subheader(f"{alum['FIRSTNAME']} {alum['LASTNAME']}")
    st.write(f"**Email:** {alum['PRIMARYEMAIL']}")
    st.write(f"**Phone:** {alum['PHONE']}")
    st.write(f"**Major:** {alum['GRAD_MAJOR']}")
    st.write(f"**Graduation Year:** {alum['ALUM_GRADYEAR']}")
    st.write(f"**Mailing List Opt-In:** {alum['MAILING_LIST']}")

    # LinkedIn profile link
    if "LINKEDIN" in alum and alum["LINKEDIN"]:
        st.write(f"**LinkedIn:** [{alum['LINKEDIN']}]({alum['LINKEDIN']})")
    else:
        st.write("**LinkedIn:** Not provided")

    tab_deg, tab_emp, tab_mem, tab_contrib = st.tabs(
        ["Degrees", "Employment", "Memberships", "Contributions"]
    )

    with tab_deg:
        st.subheader("Academic Degrees")
        deg_df = get_degrees_for_alumni(alumni_id)
        if deg_df.empty:
            st.info("No degree records for this alumni yet.")
        else:
            st.dataframe(
                deg_df[
                    ["MAJOR", "MINOR", "SCHOOL", "HONORS", "GRADMONTH", "GRADYEAR"]
                ],
                use_container_width=True,
            )

    with tab_emp:
        st.subheader("Employment History")
        emp_df = get_employment_for_alumni(alumni_id)
        if emp_df.empty:
            st.info("No employment records for this alumni yet.")
        else:
            st.dataframe(emp_df, use_container_width=True)
            st.markdown("_This highlights alumni success in the job market._")

    with tab_mem:
        st.subheader("Alumni Association Memberships")
        mem_df = get_memberships_for_alumni(alumni_id)
        if mem_df.empty:
            st.info("No memberships on record.")
        else:
            st.dataframe(mem_df, use_container_width=True)

    with tab_contrib:
        st.subheader("Contributions")
        cont_df = get_contributions_for_alumni(alumni_id)
        if cont_df.empty:
            st.info("No contributions on record.")
        else:
            st.dataframe(cont_df, use_container_width=True)
            total = cont_df["AMOUNT"].sum()
            st.write(f"**Total given by this alumni:** ${total:,.2f}")


# ---------- SESSION STATE FOR LOGIN ----------
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "alumni_id" not in st.session_state:
    st.session_state.alumni_id = None

st.sidebar.title("Portal Access")

# ---------- LOGGED OUT VIEW ----------
if st.session_state.user_role is None:
    role = st.sidebar.selectbox("I am a:", ["Student", "Admin", "Alumni"])
    username = st.sidebar.text_input(f"{role} username")
    password = st.sidebar.text_input(f"{role} password", type="password")

    if st.sidebar.button("Enter portal"):
        user = VALID_USERS.get(username)

        if user and user["password"] == password and user["role"] == role:
            st.session_state.user_role = role
            st.session_state.username = username
            st.session_state.alumni_id = user.get("alumni_id")
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials for this role. Please try again.")

    st.title("Howard University School of Business – Alumni & Student Portal")
    st.caption("Please log in as Student, Admin, or Alumni using the sidebar.")
    st.stop()

# ---------- LOGGED IN VIEW ----------
st.sidebar.write(
    f"Logged in as **{st.session_state.user_role}**"
    + (f" ({st.session_state.username})" if st.session_state.username else "")
)

if st.sidebar.button("Log out"):
    st.session_state.user_role = None
    st.session_state.username = ""
    st.session_state.alumni_id = None
    st.rerun()

# ---------- ROLE-BASED NAV ----------
if st.session_state.user_role == "Admin":
    page = st.sidebar.selectbox(
        "Navigate",
        ["Dashboard", "Alumni Directory", "Alumni Profile"],
    )
elif st.session_state.user_role == "Alumni":
    page = st.sidebar.selectbox(
        "Navigate",
        ["My Profile & Updates", "Make a Contribution", "Alumni Directory"],
    )
else:  # Student
    page = st.sidebar.selectbox(
        "Navigate",
        ["Alumni Directory"],
    )

st.title("Howard University School of Business – Alumni & Student Portal")
st.caption(
    "Demo: A central place where admins track alumni success, students discover alumni, "
    "and alumni give back and keep their information current."
)

# ============================================================
#                       PAGE HANDLERS
# ============================================================

# ---------- DASHBOARD (ADMIN) ----------
if page == "Dashboard":
    st.header("Dashboard Overview")

    stats = get_summary_stats()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Alumni", stats["total_alumni"])
    col2.metric("Total Employers", stats["total_employers"])
    col3.metric("Active Campaigns", stats["total_campaigns"])
    col4.metric("Total Contributions", f"${stats['total_contributions']:,.2f}")

    st.markdown(
        """
    ### How this supports our project goal

    This dashboard gives **administrators** a quick snapshot:

    - **Total Alumni** → how many graduates are being tracked.
    - **Total Employers** → where alumni are working.
    - **Active Campaigns** → current fundraising/engagement efforts.
    - **Total Contributions** → how much alumni have given back.
    """
    )

    st.markdown("### Drill down into the data")
    detail_view = st.radio(
        "Click a category to see details:",
        ["Alumni", "Campaigns", "Contributions by Alumni"],
        horizontal=True,
    )

    if detail_view == "Alumni":
        st.subheader("All Alumni in the System")
        alumni_df = get_alumni()
        st.dataframe(
            alumni_df[
                [
                    "ALUMNIID",
                    "FIRSTNAME",
                    "LASTNAME",
                    "PRIMARYEMAIL",
                    "ALUM_GRADYEAR",
                    "GRAD_MAJOR",
                ]
            ],
            use_container_width=True,
        )

    elif detail_view == "Campaigns":
        st.subheader("Fundraising / Engagement Campaigns")
        campaigns = get_campaigns()
        if campaigns.empty:
            st.info("No active campaigns.")
        else:
            st.dataframe(
                campaigns[["CAMPAIGNID", "CAMPAIGNNAME", "GOALAMOUNT"]],
                use_container_width=True,
            )

    elif detail_view == "Contributions by Alumni":
        st.subheader("Contributions by Alumni")
        alumni_df = get_alumni()
        rows = []
        for _, row in alumni_df.iterrows():
            aid = int(row["ALUMNIID"])
            cont_df = get_contributions_for_alumni(aid)
            total = cont_df["AMOUNT"].sum() if not cont_df.empty else 0.0
            rows.append(
                {
                    "ALUMNIID": aid,
                    "Name": f"{row['FIRSTNAME']} {row['LASTNAME']}",
                    "Grad Year": row["ALUM_GRADYEAR"],
                    "Major": row["GRAD_MAJOR"],
                    "Total Given ($)": total,
                }
            )

        contrib_summary = pd.DataFrame(rows)
        st.dataframe(contrib_summary, use_container_width=True)
        st.caption(
            "Shows which alumni are giving back and how that connects to campaigns."
        )

# ---------- ALUMNI DIRECTORY (ALL ROLES) ----------
elif page == "Alumni Directory":
    st.header("Alumni Directory")

    alumni_df = get_alumni()
    search = st.text_input("Search by last name or major")

    if not search:
        st.info("Enter a last name or major to search for alumni.")
    else:
        mask = (
            alumni_df["LASTNAME"].str.contains(search, case=False, na=False)
            | alumni_df["GRAD_MAJOR"].str.contains(search, case=False, na=False)
        )
        filtered = alumni_df[mask]

        if filtered.empty:
            st.warning("No alumni found matching that search.")
        else:
            st.write("Select an alumni below to instantly view their profile.")

            st.dataframe(
                filtered[
                    [
                        "ALUMNIID",
                        "FIRSTNAME",
                        "LASTNAME",
                        "PRIMARYEMAIL",
                        "ALUM_GRADYEAR",
                        "GRAD_MAJOR",
                    ]
                ],
                use_container_width=True,
            )

            selected_id = st.radio(
                "Choose an alumni to view profile:",
                filtered["ALUMNIID"],
                format_func=lambda x: f"{x} - {filtered[filtered['ALUMNIID'] == x]['FIRSTNAME'].iloc[0]} "
                f"{filtered[filtered['ALUMNIID'] == x]['LASTNAME'].iloc[0]}",
            )

            st.markdown("---")
            st.subheader("Alumni Profile")
            render_alumni_profile(int(selected_id))

# ---------- ALUMNI PROFILE (ADMIN NAV) ----------
elif page == "Alumni Profile":
    st.header("Alumni Profile")

    alumni_df = get_alumni().sort_values("ALUMNIID")
    selected_id = st.selectbox(
        "Select an alumni",
        alumni_df["ALUMNIID"],
        format_func=lambda x: f"{x} - {alumni_df[alumni_df['ALUMNIID'] == x]['FIRSTNAME'].iloc[0]} "
        f"{alumni_df[alumni_df['ALUMNIID'] == x]['LASTNAME'].iloc[0]}",
    )

    render_alumni_profile(int(selected_id))

# ---------- ALUMNI PAGES ----------
elif page == "My Profile & Updates" and st.session_state.user_role == "Alumni":
    st.header("My Alumni Profile & Updates")

    aid = st.session_state.alumni_id
    if not aid:
        st.error("No alumni record linked to this account (demo config issue).")
    else:
        alum_df = get_alumni_by_id(aid)
        if alum_df.empty:
            st.error("No alumni data found for this login.")
        else:
            alum = alum_df.iloc[0]

            st.subheader("Current Profile")
            st.write(f"**Name:** {alum['FIRSTNAME']} {alum['LASTNAME']}")
            st.write(f"**Graduation Year:** {alum['ALUM_GRADYEAR']}")
            st.write(f"**Major:** {alum['GRAD_MAJOR']}")

            st.markdown("### Update Contact Information")
            with st.form("update_contact"):
                email = st.text_input("Email", value=alum["PRIMARYEMAIL"])
                phone = st.text_input("Phone", value=alum["PHONE"])
                mailing = st.selectbox(
                    "Mailing list opt-in",
                    ["Yes", "No"],
                    index=0 if alum["MAILING_LIST"] == "Yes" else 1,
                )
                linkedin = st.text_input(
                    "LinkedIn Profile URL", value=alum.get("LINKEDIN", "")
                )
                submitted = st.form_submit_button("Save changes")

            if submitted:
                update_alumni_contact(int(aid), email, phone, mailing, linkedin)
                st.success("Profile updated successfully.")
                st.markdown("### Updated Profile")
                render_alumni_profile(int(aid))

            st.markdown("### My Academic & Career Snapshot")
            render_alumni_profile(int(aid))

elif page == "Make a Contribution" and st.session_state.user_role == "Alumni":
    st.header("Make a Contribution")

    aid = st.session_state.alumni_id
    if not aid:
        st.error("No alumni record linked to this account (demo config issue).")
    else:
        alum_df = get_alumni_by_id(aid)
        if not alum_df.empty:
            alum = alum_df.iloc[0]
            st.write(
                f"You are logged in as **{alum['FIRSTNAME']} {alum['LASTNAME']}** "
                f"(Class of {alum['ALUM_GRADYEAR']}, {alum['GRAD_MAJOR']})."
            )

        st.markdown(
            "Use this page to **give back to the School of Business** by "
            "supporting one of the active campaigns."
        )

        campaigns = get_campaigns()
        if campaigns.empty:
            st.info("No active campaigns available.")
        else:
            camp_lookup = {
                f"{row['CAMPAIGNNAME']} (Goal ${row['GOALAMOUNT']:,.0f})": int(
                    row["CAMPAIGNID"]
                )
                for _, row in campaigns.iterrows()
            }

            selected_campaign = st.selectbox(
                "Campaign:",
                list(camp_lookup.keys()),
            )

            amount = st.number_input(
                "Contribution Amount ($)", min_value=5.0, step=5.0
            )

            st.markdown("---")
            st.markdown("### Complete Payment via PayPal")

            # TODO: replace YOUR_PAYPAL_BUSINESS_ID with your real PayPal ID or donate link
            paypal_url = (
                "https://www.paypal.com/donate"
                f"?amount={int(amount)}&business=YOUR_PAYPAL_BUSINESS_ID"
            )

            st.markdown(
                f"""
                <a href="{paypal_url}" target="_blank">
                    <button style="padding:10px 20px; border-radius:8px;
                                   background-color:#0070ba; color:white;
                                   border:none; font-size:16px;">
                        Donate with PayPal
                    </button>
                </a>
                """,
                unsafe_allow_html=True,
            )

            st.info(
                "After you complete the payment in PayPal and return to this page, "
                "you can record the contribution in the HU database for tracking."
            )

            if st.button("Record Contribution in HU Database"):
                date_str = datetime.date.today().isoformat()
                create_contribution(
                    int(aid),
                    camp_lookup[selected_campaign],
                    float(amount),
                    date_str,
                )
                st.success(
                    "Thank you! Your contribution has been recorded in the database."
                )

                st.markdown("#### Your contribution history")
                render_alumni_profile(int(aid))
