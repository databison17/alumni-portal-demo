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
        "password": "HUSB2026!",
        "role": "Admin",
    },
    "mily.lopez@bison.howard.edu": {
        "password": "001234567",
        "role": "Student",
    },
    "maya.johnson@email.com": {
        "password": "Maya2026!",
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
            background-color: #f5f7fb;
        }

        .block-container {
            max-width: 1400px;
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }

        /* MAIN TITLES AND HEADINGS */
        h1, h2, h3, h4 {
            color: #003A63 !important;
            font-weight: 800 !important;
        }

        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4 {
            color: #003A63 !important;
            font-weight: 800 !important;
        }

        div[data-testid="stHeading"] h1,
        div[data-testid="stHeading"] h2,
        div[data-testid="stHeading"] h3 {
            color: #003A63 !important;
            font-weight: 800 !important;
        }

        .hero-card {
            background: linear-gradient(135deg, #003A63 0%, #0a4d81 100%);
            color: white;
            border-radius: 20px;
            padding: 1.6rem 1.8rem;
            box-shadow: 0 10px 24px rgba(0, 58, 99, 0.20);
            margin-bottom: 1rem;
        }

        .hero-title {
            color: white !important;
            font-size: 2.7rem;
            font-weight: 700;
            line-height: 1.05;
            margin-bottom: 0.4rem;
        }

        .hero-subtitle {
            color: rgba(255, 255, 255, 0.95) !important;
            font-size: 1rem;
            line-height: 1.6;
        }

        .hero-accent {
            height: 5px;
            width: 90px;
            background: #E51937;
            border-radius: 999px;
            margin-bottom: 0.85rem;
        }

        .section-card {
            background: white;
            border-radius: 18px;
            padding: 1.2rem;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
            border-left: 6px solid #E51937;
            margin-bottom: 1rem;
        }

        .section-card h2,
        .section-card h3,
        .section-card h4 {
            color: #003A63 !important;
            font-weight: 800 !important;
            margin-top: 0.1rem;
            margin-bottom: 0.75rem;
        }

        .kpi-card {
            background: white;
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
            border-top: 5px solid #E51937;
            min-height: 115px;
            text-align: center;
        }

        .kpi-label {
            color: #667085;
            font-size: 0.95rem;
            margin-bottom: 0.3rem;
        }

        .kpi-value {
            color: #003A63;
            font-size: 2rem;
            font-weight: 800;
        }

        .profile-chip {
            display: inline-block;
            background: #fff2f4;
            color: #E51937;
            border: 1px solid #ffd1d9;
            border-radius: 999px;
            padding: 0.33rem 0.75rem;
            margin-right: 0.4rem;
            margin-bottom: 0.45rem;
            font-size: 0.9rem;
        }

        .muted-text {
            color: #5f6b7a;
            font-size: 0.95rem;
            line-height: 1.65;
        }

        .small-note {
            color: #667085;
            font-size: 0.9rem;
        }

        .info-divider {
            border: none;
            border-top: 1px solid #e5e7eb;
            margin: 0.5rem 0 1rem 0;
        }

        .paypal-card {
            background: linear-gradient(135deg, #ffffff 0%, #f9fbff 100%);
            border: 1px solid #dbe7f3;
            border-left: 5px solid #E51937;
            border-radius: 18px;
            padding: 1.1rem;
            margin-top: 0.75rem;
            margin-bottom: 1rem;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
        }

        .paypal-button {
            display: inline-block;
            background-color: #0070ba;
            color: white !important;
            text-decoration: none;
            padding: 12px 20px;
            border-radius: 10px;
            font-weight: 700;
            font-size: 15px;
            border: none;
        }

        .paypal-button:hover {
            background-color: #005ea6;
            color: white !important;
        }

        /* SIDEBAR */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #003A63 0%, #002b49 100%);
        }

        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }

        .sidebar-header {
            display: block;
            background: #E51937;
            color: #ffffff !important;
            font-weight: 800;
            font-size: 1rem;
            padding: 0.6rem 0.85rem;
            border-radius: 10px;
            margin: 0.35rem 0 0.6rem 0;
            letter-spacing: 0.2px;
        }

        .sidebar-box {
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 12px;
            padding: 0.85rem 0.9rem;
            margin-bottom: 0.85rem;
            color: #ffffff !important;
            line-height: 1.75;
            font-size: 0.96rem;
        }

        [data-testid="stSidebar"] label {
            color: #ffffff !important;
            font-weight: 700 !important;
            opacity: 1 !important;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label p,
        [data-testid="stSidebar"] [role="radiogroup"] label span,
        [data-testid="stSidebar"] .stRadio label p,
        [data-testid="stSidebar"] .stRadio label span {
            color: #ffffff !important;
            font-weight: 600 !important;
            opacity: 1 !important;
        }

        .stButton > button {
            background-color: #E51937;
            color: white;
            border-radius: 10px;
            border: none;
            font-weight: 700;
        }

        .stButton > button:hover {
            background-color: #c6132d;
            color: white;
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
    st.markdown(
        f'<div class="section-card"><h3 style="color:#003A63; font-weight:800;">{title}</h3>',
        unsafe_allow_html=True,
    )


def render_section_close():
    st.markdown("</div>", unsafe_allow_html=True)


def alumni_name_from_df(df: pd.DataFrame, alumni_id: int) -> str:
    row = df[df["ALUMNIID"] == alumni_id].iloc[0]
    return f"{row['FIRSTNAME']} {row['LASTNAME']}"


def render_top_brand():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Howard University Alumni Portal</div>
            <div class="hero-accent"></div>
            <div class="hero-subtitle">
                A centralized alumni subsystem for records management, engagement,
                reporting, and contributions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_alumni_summary(alum: pd.Series):
    st.markdown(
        f"""
        <div class="section-card">
            <h2 style="margin-bottom: 0.45rem; color:#003A63; font-weight:800;">
                {alum['FIRSTNAME']} {alum['LASTNAME']}
            </h2>
            <div class="muted-text" style="margin-bottom: 0.85rem;">
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
            display_cols = [
                c for c in ["MAJOR", "MINOR", "SCHOOL", "HONORS", "GRADMONTH", "GRADYEAR"]
                if c in deg_df.columns
            ]
            st.dataframe(deg_df[display_cols], use_container_width=True, hide_index=True)
        render_section_close()

    with tab_employment:
        render_section_open("Employment History")
        emp_df = get_employment_for_alumni(alumni_id)
        if emp_df.empty:
            st.info("No employment records available.")
        else:
            st.dataframe(emp_df, use_container_width=True, hide_index=True)
            st.caption("This supports employer tracking, networking, and alumni career analytics.")
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
        render_section_open("Contribution History")
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
    st.sidebar.markdown('<div class="sidebar-header">Portal Access</div>', unsafe_allow_html=True)

    role = st.sidebar.selectbox("I am logging in as", ["Student", "Admin", "Alumni"])
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Enter Portal", use_container_width=True):
        user = VALID_USERS.get(username)
        if user and user["password"] == password and user["role"] == role:
            st.session_state.user_role = role
            st.session_state.username = username
            st.session_state.alumni_id = user.get("alumni_id")
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials for this role.")

    render_top_brand()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Welcome")
        st.write(
            "This portal demonstrates a Howard University Alumni Subsystem designed to support:"
        )
        st.markdown(
            """
- Centralized alumni records
- Employment and membership tracking
- Contribution and campaign management
- Mailing lists and reporting support
            """
        )
        st.caption(
            "Use the sidebar to enter the demo portal as an Admin, Student, or Alumni user."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Demo Accounts")

        st.markdown("**Admin**")
        st.write("Username: admin")
        st.write("Password: HUSB2026!")

        st.markdown("**Student**")
        st.write("Username: mily.lopez@bison.howard.edu")
        st.write("Password: 001234567")

        st.markdown("**Alumni**")
        st.write("Username: maya.johnson@email.com")
        st.write("Password: Maya2026!")

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ---------------------------------------------------------
# AUTH
# ---------------------------------------------------------
if st.session_state.user_role is None:
    render_login()

# ---------------------------------------------------------
# SIDEBAR AFTER LOGIN
# ---------------------------------------------------------
st.sidebar.markdown('<div class="sidebar-header">Session</div>', unsafe_allow_html=True)
st.sidebar.markdown(
    f"""
    <div class="sidebar-box">
        <b>Logged in as:</b> {st.session_state.user_role}<br>
        <b>User:</b> {st.session_state.username}
    </div>
    """,
    unsafe_allow_html=True,
)

if st.sidebar.button("Log Out", use_container_width=True):
    st.session_state.user_role = None
    st.session_state.username = ""
    st.session_state.alumni_id = None
    st.rerun()

st.sidebar.markdown('<div class="sidebar-header">Navigate</div>', unsafe_allow_html=True)

if st.session_state.user_role == "Admin":
    page = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Alumni Directory", "Alumni Profile", "Reports"],
    )
elif st.session_state.user_role == "Alumni":
    page = st.sidebar.radio(
        "Menu",
        ["My Profile & Updates", "Make a Contribution", "Alumni Directory"],
    )
else:
    page = st.sidebar.radio(
        "Menu",
        ["Alumni Directory"],
    )

# ---------------------------------------------------------
# MAIN BRAND
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

    st.markdown("<hr class='info-divider'>", unsafe_allow_html=True)

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

    render_section_open("Dashboard Purpose")
    st.write(
        "This dashboard gives administrators a quick overview of alumni records, campaign activity, employer reach, and contribution totals."
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
            search_name = st.text_input("Search by first or last name")
        with c2:
            search_major = st.text_input("Search by major")
        with c3:
            grad_years = ["All"] + sorted(
                alumni_df["ALUM_GRADYEAR"].dropna().astype(int).unique().tolist()
            )
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

        display_cols = [
            c for c in
            ["ALUMNIID", "FIRSTNAME", "LASTNAME", "PRIMARYEMAIL", "ALUM_GRADYEAR", "GRAD_MAJOR"]
            if c in filtered.columns
        ]
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
            mail_df = mail_df[
                mail_df["GRAD_MAJOR"].str.contains(major_filter, case=False, na=False)
            ]
        if year_filter != "All":
            mail_df = mail_df[mail_df["ALUM_GRADYEAR"] == year_filter]

        if mail_df.empty:
            st.info("No mailing list results for the selected filters.")
        else:
            export_cols = [
                c for c in
                ["FIRSTNAME", "LASTNAME", "PRIMARYEMAIL", "ALUM_GRADYEAR", "GRAD_MAJOR", "MAILING_LIST"]
                if c in mail_df.columns
            ]
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

            c1, c2 = st.columns([1.15, 1])

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
                render_section_open("Why This Matters")
                st.write(
                    "Keeping alumni information current supports better communication, networking, engagement, and fundraising accuracy."
                )
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

        render_section_open("Give Back to Howard University")
        st.write(
            "Alumni can support scholarships, student success initiatives, and other approved university causes through this donation area."
        )

        donation_type = st.selectbox(
            "Choose what you would like to support",
            [
                "Scholarship Fund",
                "Student Emergency Support",
                "Study Abroad Support",
                "General Alumni Giving",
                "Existing Campaign",
                "Specific Student / Custom Purpose",
            ],
        )

        custom_note = ""
        if donation_type == "Existing Campaign":
            if campaigns.empty:
                st.info("No campaigns are available at the moment.")
                selected_campaign_label = None
                selected_campaign_id = None
            else:
                camp_lookup = {
                    f"{row['CAMPAIGNNAME']} (Goal ${row['GOALAMOUNT']:,.0f})": int(row["CAMPAIGNID"])
                    for _, row in campaigns.iterrows()
                }
                selected_campaign_label = st.selectbox("Select a campaign", list(camp_lookup.keys()))
                selected_campaign_id = camp_lookup[selected_campaign_label]
        else:
            selected_campaign_label = donation_type
            selected_campaign_id = None

        if donation_type == "Specific Student / Custom Purpose":
            custom_note = st.text_area(
                "Enter the student name, scholarship name, or custom giving purpose",
                placeholder="Example: Manuel Ray Lopez Scholarship / Senior Leadership Scholarship / Emergency support for a student initiative",
            )

        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("Contribution Amount ($)", min_value=5.0, step=5.0)
        with col2:
            donor_name = st.text_input(
                "Display Name",
                value=f"{alum['FIRSTNAME']} {alum['LASTNAME']}" if not alum_df.empty else "",
            )

        purpose_text = selected_campaign_label if selected_campaign_label else donation_type
        if custom_note.strip():
            purpose_text = f"{purpose_text} - {custom_note.strip()}"

        st.markdown(
            f"""
            <div class="paypal-card">
                <h3 style="margin-bottom:0.4rem; color:#003A63; font-weight:800;">PayPal Donation</h3>
                <p class="muted-text" style="margin-bottom:0.8rem;">
                    <b>Donor:</b> {donor_name}<br>
                    <b>Purpose:</b> {purpose_text}<br>
                    <b>Amount:</b> ${amount:,.2f}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        PAYPAL_BUSINESS_ID = "YOUR_PAYPAL_BUSINESS_ID"

        paypal_url = (
            "https://www.paypal.com/donate"
            f"?business={PAYPAL_BUSINESS_ID}"
            f"&amount={amount:.2f}"
            f"&item_name={purpose_text.replace(' ', '%20')}"
            f"&currency_code=USD"
        )

        st.markdown(
            f"""
            <a href="{paypal_url}" target="_blank" class="paypal-button">
                💳 Donate with PayPal
            </a>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            "After completing payment in PayPal, return here and record the contribution in the alumni database for reporting and campaign tracking."
        )

        if st.button("Record Contribution in Alumni Database", use_container_width=True):
            date_str = datetime.date.today().isoformat()

            if selected_campaign_id is None:
                if not campaigns.empty:
                    selected_campaign_id = int(campaigns.iloc[0]["CAMPAIGNID"])
                else:
                    st.error("No campaign exists in the database to attach this contribution to.")
                    st.stop()

            create_contribution(
                int(aid),
                int(selected_campaign_id),
                float(amount),
                date_str,
            )
            st.success("Thank you. Your contribution has been recorded successfully.")
            st.balloons()

        render_section_close()

        render_section_open("My Contribution History")
        cont_df = get_contributions_for_alumni(int(aid))
        if cont_df.empty:
            st.info("No contribution history available yet.")
        else:
            st.dataframe(cont_df, use_container_width=True, hide_index=True)
            total = float(cont_df["AMOUNT"].sum()) if "AMOUNT" in cont_df.columns else 0.0
            st.success(f"Total Contributions: ${total:,.2f}")
        render_section_close()
