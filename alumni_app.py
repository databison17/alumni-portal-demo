import datetime
import pandas as pd
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
    get_employer_summary,
    get_campaigns,
    get_all_contributions,
    update_alumni_contact,
    create_contribution,
)

# ---------------------------------------------------------
# PAGE CONFIG + DB INIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Howard University Alumni Portal",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ---------------------------------------------------------
# DEMO USERS
# ---------------------------------------------------------
VALID_USERS = {
    "admin": {
        "password": "HUSB2024!",
        "role": "Admin",
    },
    "mily.lopez@bison.howard.edu": {
        "password": "001234567",
        "role": "Student",
    },
    "maya.johnson@email.com": {
        "password": "Maya2024!",
        "role": "Alumni",
        "alumni_id": 1001,
    },
}

# ---------------------------------------------------------
# CUSTOM STYLING
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background-color: #f6f8fb;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }

        h1, h2, h3 {
            color: #002147;
        }

        .hero-card {
            background: linear-gradient(135deg, #002147 0%, #123b73 100%);
            color: white;
            border-radius: 18px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1rem;
            box-shadow: 0 8px 24px rgba(0, 33, 71, 0.18);
        }

        .section-card {
            background: white;
            border-radius: 16px;
            padding: 1rem 1rem 0.75rem 1rem;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
            border: 1px solid #edf1f7;
            margin-bottom: 1rem;
        }

        .kpi-card {
            background: white;
            border-radius: 16px;
            padding: 1rem 1rem 0.75rem 1rem;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
            border: 1px solid #edf1f7;
            min-height: 120px;
        }

        .kpi-label {
            color: #5b6575;
            font-size: 0.95rem;
            margin-bottom: 0.3rem;
        }

        .kpi-value {
            color: #002147;
            font-size: 1.85rem;
            font-weight: 700;
        }

        .profile-chip {
            display: inline-block;
            background: #eef4ff;
            color: #123b73;
            border: 1px solid #d8e5ff;
            border-radius: 999px;
            padding: 0.25rem 0.7rem;
            margin-right: 0.45rem;
            margin-bottom: 0.45rem;
            font-size: 0.9rem;
        }

        .small-muted {
            color: #667085;
            font-size: 0.92rem;
        }

        .sidebar-title {
            color: white;
            font-weight: 700;
            font-size: 1.05rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #002147 0%, #0d2f5c 100%);
        }

        [data-testid="stSidebar"] * {
            color: white !important;
        }

        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stRadio label,
        [data-testid="stSidebar"] .stTextInput label {
            color: white !important;
        }

        .divider-space {
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "alumni_id" not in st.session_state:
    st.session_state.alumni_id = None

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def render_top_brand():
    left, right = st.columns([6, 1])
    with left:
        st.markdown(
            """
            <div class="hero-card">
                <h1 style="margin-bottom: 0.2rem; color: white;">Howard University Alumni Portal</h1>
                <div style="font-size: 1rem; opacity: 0.95;">
                    A centralized alumni subsystem for records management, engagement, reporting, and contributions.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.empty()


def render_kpi_card(label: str, value: str):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_open(title: str):
    st.markdown(f'<div class="section-card"><h3>{title}</h3>', unsafe_allow_html=True)


def render_section_close():
    st.markdown("</div>", unsafe_allow_html=True)


def alumni_name_from_df(df: pd.DataFrame, alumni_id: int) -> str:
    row = df[df["ALUMNIID"] == alumni_id].iloc[0]
    return f"{row['FIRSTNAME']} {row['LASTNAME']}"


def render_alumni_summary(alum: pd.Series):
    st.markdown(
        f"""
        <div class="section-card">
            <h2 style="margin-bottom: 0.35rem;">{alum['FIRSTNAME']} {alum['LASTNAME']}</h2>
            <div class="small-muted" style="margin-bottom: 0.65rem;">
                Howard University School of Business Alumni Profile
            </div>
            <span class="profile-chip">Email: {alum['PRIMARYEMAIL']}</span>
            <span class="profile-chip">Phone: {alum['PHONE'] or 'N/A'}</span>
            <span class="profile-chip">Major: {alum['GRAD_MAJOR'] or 'N/A'}</span>
            <span class="profile-chip">Grad Year: {alum['ALUM_GRADYEAR'] or 'N/A'}</span>
            <span class="profile-chip">Mailing List: {alum['MAILING_LIST']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "LINKEDIN" in alum.index and alum["LINKEDIN"]:
        st.markdown(f"[View LinkedIn Profile]({alum['LINKEDIN']})")


def render_alumni_profile(alumni_id: int):
    alum_df = get_alumni_by_id(alumni_id)
    if alum_df.empty:
        st.error("Alumni not found.")
        return

    alum = alum_df.iloc[0]
    render_alumni_summary(alum)

    tab_overview, tab_degrees, tab_employment, tab_memberships, tab_contributions = st.tabs(
        ["Overview", "Degrees", "Employment", "Memberships", "Contributions"]
    )

    with tab_overview:
        c1, c2 = st.columns(2)
        with c1:
            render_section_open("Contact Information")
            st.write(f"**Primary Email:** {alum['PRIMARYEMAIL']}")
            st.write(f"**Phone:** {alum['PHONE'] or 'N/A'}")
            st.write(f"**Mailing List Opt-In:** {alum['MAILING_LIST']}")
            render_section_close()
        with c2:
            render_section_open("Academic Snapshot")
            st.write(f"**Major:** {alum['GRAD_MAJOR'] or 'N/A'}")
            st.write(f"**Graduation Year:** {alum['ALUM_GRADYEAR'] or 'N/A'}")
            render_section_close()

    with tab_degrees:
        render_section_open("Academic Degrees")
        deg_df = get_degrees_for_alumni(alumni_id)
        if deg_df.empty:
            st.info("No degree records available.")
        else:
            display_cols = [c for c in ["MAJOR", "MINOR", "SCHOOL", "HONORS", "GRADMONTH", "GRADYEAR"] if c in deg_df.columns]
            st.dataframe(deg_df[display_cols], use_container_width=True, hide_index=True)
        render_section_close()

    with tab_employment:
        render_section_open("Employment History")
        emp_df = get_employment_for_alumni(alumni_id)
        if emp_df.empty:
            st.info("No employment records available.")
        else:
            st.dataframe(emp_df, use_container_width=True, hide_index=True)
            st.caption("This view supports employer tracking, networking, and alumni career analytics.")
        render_section_close()

    with tab_memberships:
        render_section_open("Association Memberships")
        mem_df = get_memberships_for_alumni(alumni_id)
        if mem_df.empty:
            st.info("No membership records available.")
        else:
            st.dataframe(mem_df, use_container_width=True, hide_index=True)
        render_section_close()

    with tab_contributions:
        render_section_open("Contributions")
        cont_df = get_contributions_for_alumni(alumni_id)
        if cont_df.empty:
            st.info("No contribution history available.")
        else:
            st.dataframe(cont_df, use_container_width=True, hide_index=True)
            if "AMOUNT" in cont_df.columns:
                total = float(cont_df["AMOUNT"].sum())
                st.success(f"Total Contributions: ${total:,.2f}")
        render_section_close()


def render_login():
    st.sidebar.markdown('<div class="sidebar-title">Portal Access</div>', unsafe_allow_html=True)
    role = st.sidebar.selectbox("I am logging in as", ["Student", "Admin", "Alumni"])
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    render_top_brand()

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown(
            """
            <div class="section-card">
                <h2>Welcome</h2>
                <p class="small-muted">
                    This portal demonstrates a university alumni subsystem that supports:
                </p>
                <ul>
                    <li>Centralized alumni records</li>
                    <li>Employment and membership tracking</li>
                    <li>Contribution and campaign management</li>
                    <li>Mailing lists and reporting support</li>
                </ul>
                <p class="small-muted">
                    Use the sidebar to enter the demo portal as an Admin, Student, or Alumni user.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="section-card">
                <h3>Demo Accounts</h3>
                <p><b>Admin</b><br>Username: admin<br>Password: HUSB2024!</p>
                <p><b>Student</b><br>Username: mily.lopez@bison.howard.edu<br>Password: 001234567</p>
                <p><b>Alumni</b><br>Username: maya.johnson@email.com<br>Password: Maya2024!</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.sidebar.button("Enter Portal", use_container_width=True):
        user = VALID_USERS.get(username)
        if user and user["password"] == password and user["role"] == role:
            st.session_state.user_role = role
            st.session_state.username = username
            st.session_state.alumni_id = user.get("alumni_id")
            st.rerun()
        st.sidebar.error("Invalid credentials for this role.")

    st.stop()


# ---------------------------------------------------------
# AUTH
# ---------------------------------------------------------
if st.session_state.user_role is None:
    render_login()

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.markdown('<div class="sidebar-title">Session</div>', unsafe_allow_html=True)
st.sidebar.write(f"Logged in as **{st.session_state.user_role}**")
if st.session_state.username:
    st.sidebar.caption(st.session_state.username)

if st.sidebar.button("Log Out", use_container_width=True):
    st.session_state.user_role = None
    st.session_state.username = ""
    st.session_state.alumni_id = None
    st.rerun()

st.sidebar.markdown("---")

if st.session_state.user_role == "Admin":
    page = st.sidebar.radio(
        "Navigate",
        ["Dashboard", "Alumni Directory", "Alumni Profile", "Reports"],
    )
elif st.session_state.user_role == "Alumni":
    page = st.sidebar.radio(
        "Navigate",
        ["My Profile & Updates", "Make a Contribution", "Alumni Directory"],
    )
else:
    page = st.sidebar.radio(
        "Navigate",
        ["Alumni Directory"],
    )

# ---------------------------------------------------------
# MAIN HEADER
# ---------------------------------------------------------
render_top_brand()

# ---------------------------------------------------------
# PAGES
# ---------------------------------------------------------
if page == "Dashboard":
    st.subheader("Administrative Dashboard")

    stats = get_summary_stats()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Total Alumni", f"{stats['total_alumni']:,}")
    with c2:
        render_kpi_card("Employers Represented", f"{stats['total_employers']:,}")
    with c3:
        render_kpi_card("Active Campaigns", f"{stats['total_campaigns']:,}")
    with c4:
        render_kpi_card("Total Contributions", f"${stats['total_contributions']:,.0f}")

    st.markdown("<div class='divider-space'></div>", unsafe_allow_html=True)

    left, right = st.columns([1.2, 1])

    with left:
        render_section_open("Contribution Trends")
        contrib_df = get_all_contributions()
        if contrib_df.empty:
            st.info("No contribution data available yet.")
        else:
            if "CONTRIBUTIONDATE" in contrib_df.columns:
                contrib_df["CONTRIBUTIONDATE"] = pd.to_datetime(contrib_df["CONTRIBUTIONDATE"])
                trend = (
                    contrib_df.groupby("CONTRIBUTIONDATE", as_index=False)["AMOUNT"]
                    .sum()
                    .sort_values("CONTRIBUTIONDATE")
                )
                trend = trend.set_index("CONTRIBUTIONDATE")
                st.line_chart(trend["AMOUNT"], use_container_width=True)
            st.dataframe(contrib_df, use_container_width=True, hide_index=True)
        render_section_close()

    with right:
        render_section_open("Employer Summary")
        emp_summary = get_employer_summary()
        if emp_summary.empty:
            st.info("No employer summary available.")
        else:
            st.dataframe(emp_summary, use_container_width=True, hide_index=True)
        render_section_close()

    render_section_open("Administrative Use")
    st.write(
        "This dashboard gives administrators a quick overview of alumni records, employer reach, campaign activity, and contribution totals."
    )
    render_section_close()

elif page == "Alumni Directory":
    st.subheader("Alumni Directory")

    alumni_df = get_alumni()
    if alumni_df.empty:
        st.warning("No alumni records available.")
    else:
        render_section_open("Search and Filter")
        c1, c2, c3 = st.columns(3)
        with c1:
            search_name = st.text_input("Search by last name")
        with c2:
            search_major = st.text_input("Search by major")
        with c3:
            grad_years = ["All"] + sorted(alumni_df["ALUM_GRADYEAR"].dropna().astype(int).unique().tolist())
            selected_grad_year = st.selectbox("Graduation year", grad_years)

        filtered = alumni_df.copy()

        if search_name:
            filtered = filtered[
                filtered["LASTNAME"].str.contains(search_name, case=False, na=False)
                | filtered["FIRSTNAME"].str.contains(search_name, case=False, na=False)
            ]

        if search_major:
            filtered = filtered[
                filtered["GRAD_MAJOR"].str.contains(search_major, case=False, na=False)
            ]

        if selected_grad_year != "All":
            filtered = filtered[filtered["ALUM_GRADYEAR"] == selected_grad_year]

        display_cols = [c for c in ["ALUMNIID", "FIRSTNAME", "LASTNAME", "PRIMARYEMAIL", "ALUM_GRADYEAR", "GRAD_MAJOR"] if c in filtered.columns]
        st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)
        render_section_close()

        if filtered.empty:
            st.warning("No alumni matched your search.")
        else:
            selected_id = st.selectbox(
                "Select an alumni profile to view",
                filtered["ALUMNIID"].tolist(),
                format_func=lambda x: f"{x} - {alumni_name_from_df(filtered, x)}",
            )
            render_alumni_profile(int(selected_id))

elif page == "Alumni Profile":
    st.subheader("Alumni Profile Viewer")

    alumni_df = get_alumni().sort_values("ALUMNIID")
    if alumni_df.empty:
        st.warning("No alumni records available.")
    else:
        selected_id = st.selectbox(
            "Select an alumni",
            alumni_df["ALUMNIID"].tolist(),
            format_func=lambda x: f"{x} - {alumni_name_from_df(alumni_df, x)}",
        )
        render_alumni_profile(int(selected_id))

elif page == "Reports":
    st.subheader("Reports and Mailing List Support")

    alumni_df = get_alumni()
    contrib_df = get_all_contributions()
    campaigns_df = get_campaigns()

    tab1, tab2, tab3 = st.tabs(["Mailing List", "Contribution Report", "Campaign Report"])

    with tab1:
        render_section_open("Generate Mailing List")
        major_filter = st.text_input("Filter by major", key="mail_major")
        year_options = ["All"]
        if not alumni_df.empty and "ALUM_GRADYEAR" in alumni_df.columns:
            year_options += sorted(alumni_df["ALUM_GRADYEAR"].dropna().astype(int).unique().tolist())
        year_filter = st.selectbox("Filter by graduation year", year_options, key="mail_year")

        mail_df = alumni_df.copy()
        if major_filter:
            mail_df = mail_df[mail_df["GRAD_MAJOR"].str.contains(major_filter, case=False, na=False)]
        if year_filter != "All":
            mail_df = mail_df[mail_df["ALUM_GRADYEAR"] == year_filter]

        if mail_df.empty:
            st.info("No mailing list results for the selected filters.")
        else:
            export_cols = [c for c in ["FIRSTNAME", "LASTNAME", "PRIMARYEMAIL", "ALUM_GRADYEAR", "GRAD_MAJOR", "MAILING_LIST"] if c in mail_df.columns]
            st.dataframe(mail_df[export_cols], use_container_width=True, hide_index=True)
            csv = mail_df[export_cols].to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Mailing List CSV",
                data=csv,
                file_name="mailing_list.csv",
                mime="text/csv",
            )
        render_section_close()

    with tab2:
        render_section_open("Contribution Report")
        if contrib_df.empty:
            st.info("No contribution report available.")
        else:
            st.dataframe(contrib_df, use_container_width=True, hide_index=True)
            total = contrib_df["AMOUNT"].sum() if "AMOUNT" in contrib_df.columns else 0
            st.success(f"Total Contributions Across All Campaigns: ${total:,.2f}")
        render_section_close()

    with tab3:
        render_section_open("Campaign Report")
        if campaigns_df.empty:
            st.info("No campaign records available.")
        else:
            st.dataframe(campaigns_df, use_container_width=True, hide_index=True)
        render_section_close()

elif page == "My Profile & Updates" and st.session_state.user_role == "Alumni":
    st.subheader("My Profile and Updates")

    aid = st.session_state.alumni_id
    if not aid:
        st.error("No alumni record is linked to this account.")
    else:
        alum_df = get_alumni_by_id(aid)
        if alum_df.empty:
            st.error("No alumni data found for this account.")
        else:
            alum = alum_df.iloc[0]
            render_alumni_summary(alum)

            c1, c2 = st.columns([1.1, 1])
            with c1:
                render_section_open("Update Contact Information")
                with st.form("update_contact_form"):
                    email = st.text_input("Primary Email", value=alum["PRIMARYEMAIL"])
                    phone = st.text_input("Phone", value=alum["PHONE"] or "")
                    mailing = st.selectbox(
                        "Mailing List Preference",
                        ["Yes", "No"],
                        index=0 if str(alum["MAILING_LIST"]) == "Yes" else 1,
                    )
                    submitted = st.form_submit_button("Save Changes", use_container_width=True)

                if submitted:
                    update_alumni_contact(int(aid), email, phone, mailing)
                    st.success("Your profile was updated successfully.")
                    st.rerun()
                render_section_close()

            with c2:
                render_section_open("Profile Summary")
                st.write("Keep your alumni record current so the university can maintain accurate outreach, networking, and fundraising information.")
                render_section_close()

            render_alumni_profile(int(aid))

elif page == "Make a Contribution" and st.session_state.user_role == "Alumni":
    st.subheader("Make a Contribution")

    aid = st.session_state.alumni_id
    if not aid:
        st.error("No alumni record is linked to this account.")
    else:
        alum_df = get_alumni_by_id(aid)
        if not alum_df.empty:
            alum = alum_df.iloc[0]
            render_alumni_summary(alum)

        campaigns = get_campaigns()
        if campaigns.empty:
            st.info("There are no active campaigns available right now.")
        else:
            render_section_open("Support Howard University")
            st.write("Select a campaign and contribution amount below.")

            camp_lookup = {
                f"{row['CAMPAIGNNAME']} (Goal ${row['GOALAMOUNT']:,.0f})": int(row["CAMPAIGNID"])
                for _, row in campaigns.iterrows()
            }

            c1, c2 = st.columns(2)
            with c1:
                selected_campaign = st.selectbox("Campaign", list(camp_lookup.keys()))
            with c2:
                amount = st.number_input("Contribution Amount ($)", min_value=5.0, step=5.0)

            st.markdown("### PayPal Donation Link")
            paypal_url = (
                "https://www.paypal.com/donate?"
                f"amount={int(amount)}&business=YOUR_PAYPAL_BUSINESS_ID"
            )

            st.markdown(
                f"""
                <a href="{paypal_url}" target="_blank">
                    <button style="padding:10px 20px; border-radius:10px; background-color:#0070ba; color:white; border:none; font-size:16px; cursor:pointer;">
                        Donate with PayPal
                    </button>
                </a>
                """,
                unsafe_allow_html=True,
            )

            st.info(
                "After completing the payment, click the button below to record the contribution in the university database."
            )

            if st.button("Record Contribution in Alumni Database", use_container_width=True):
                date_str = datetime.date.today().isoformat()
                create_contribution(int(aid), camp_lookup[selected_campaign], float(amount), date_str)
                st.success("Thank you. Your contribution has been recorded successfully.")
                st.balloons()

            render_section_close()

            render_section_open("My Contribution History")
            render_alumni_profile(int(aid))
            render_section_close()
