import pandas as pd
from sqlalchemy import create_engine, text

# -------------------------------------------------------------------
# SQLite Engine
# -------------------------------------------------------------------
engine = create_engine("sqlite:///alumni.db", echo=False, future=True)


# -------------------------------------------------------------------
#  CREATE TABLES + SEED DATA
# -------------------------------------------------------------------
def init_db():
    """Create tables and insert demo data if empty."""
    with engine.begin() as conn:
        # --------------------------
        # ALUMNI TABLE
        # --------------------------
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ALUMNI (
                ALUMNIID      INTEGER PRIMARY KEY,
                FIRSTNAME     TEXT NOT NULL,
                LASTNAME      TEXT NOT NULL,
                PRIMARYEMAIL  TEXT NOT NULL,
                PHONE         TEXT,
                GRAD_MAJOR    TEXT,
                ALUM_GRADYEAR INTEGER,
                MAILING_LIST  TEXT,
                LINKEDIN      TEXT
            );
        """))

        # --------------------------
        # DEGREE TABLE
        # --------------------------
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS DEGREE (
                DEGREEID  INTEGER PRIMARY KEY,
                ALUMNIID  INTEGER NOT NULL,
                MAJOR     TEXT,
                MINOR     TEXT,
                SCHOOL    TEXT,
                HONORS    TEXT,
                GRADMONTH TEXT,
                GRADYEAR  INTEGER
            );
        """))

        # --------------------------
        # EMPLOYMENT TABLE
        # --------------------------
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS EMPLOYMENT (
                EMPLOYMENTID INTEGER PRIMARY KEY,
                ALUMNIID     INTEGER NOT NULL,
                EMPLOYERNAME TEXT,
                INDUSTRY     TEXT,
                POSITION     TEXT,
                STARTYEAR    INTEGER,
                ENDYEAR      INTEGER
            );
        """))

        # --------------------------
        # ALUMNI MEMBERSHIP TABLE
        # --------------------------
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ALUMNI_MEMBERSHIP (
                MEMBERID    INTEGER PRIMARY KEY,
                ALUMNIID    INTEGER NOT NULL,
                ORGANIZATION TEXT,
                ROLE        TEXT,
                STARTYEAR   INTEGER,
                ENDYEAR     INTEGER
            );
        """))

        # --------------------------
        # CAMPAIGN TABLE
        # --------------------------
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS CAMPAIGN (
                CAMPAIGNID   INTEGER PRIMARY KEY,
                CAMPAIGNNAME TEXT,
                GOALAMOUNT   REAL,
                STATUS       TEXT
            );
        """))

        # --------------------------
        # CONTRIBUTION TABLE
        # --------------------------
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS CONTRIBUTION (
                CONTRIBUTIONID   INTEGER PRIMARY KEY,
                ALUMNIID         INTEGER NOT NULL,
                CAMPAIGNID       INTEGER NOT NULL,
                CONTRIBUTIONDATE TEXT,
                AMOUNT           REAL
            );
        """))

    seed_demo_data()
    ensure_linkedin_column_and_demo_data()


# -------------------------------------------------------------------
#  ENSURE LINKEDIN COLUMN + DEMO VALUE
# -------------------------------------------------------------------
def ensure_linkedin_column_and_demo_data():
    """Make sure ALUMNI has a LINKEDIN column and a demo URL for Maya."""
    with engine.begin() as conn:
        cols = conn.execute(text("PRAGMA table_info(ALUMNI);")).fetchall()
        col_names = [c[1] for c in cols]

        # Add LINKEDIN column if missing
        if "LINKEDIN" not in col_names:
            conn.execute(text("ALTER TABLE ALUMNI ADD COLUMN LINKEDIN TEXT;"))

        # Give Maya Johnson (ALUMNIID 1001) a demo LinkedIn URL if blank
        conn.execute(text("""
            UPDATE ALUMNI
            SET LINKEDIN = 'https://www.linkedin.com/in/maya-johnson-demo'
            WHERE ALUMNIID = 1001
              AND (LINKEDIN IS NULL OR LINKEDIN = '');
        """))


# -------------------------------------------------------------------
#  SEED DEMO DATA (ONLY IF ALUMNI TABLE IS EMPTY)
# -------------------------------------------------------------------
def seed_demo_data():
    with engine.begin() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM ALUMNI")).scalar()
        if count and count > 0:
            return  # already seeded

        # Example single alumni (Maya Johnson)
        conn.execute(text("""
            INSERT INTO ALUMNI (
                ALUMNIID, FIRSTNAME, LASTNAME,
                PRIMARYEMAIL, PHONE,
                GRAD_MAJOR, ALUM_GRADYEAR,
                MAILING_LIST, LINKEDIN
            )
            VALUES (
                1001, 'Maya', 'Johnson',
                'maya.johnson@email.com', '202-555-7821',
                'Finance', 2018,
                'Yes', ''
            );
        """))

        # Degree
        conn.execute(text("""
            INSERT INTO DEGREE (
                DEGREEID, ALUMNIID, MAJOR, MINOR,
                SCHOOL, HONORS, GRADMONTH, GRADYEAR
            )
            VALUES (
                1, 1001, 'Finance', 'None',
                'Howard University School of Business',
                'Cum Laude', 'May', 2018
            );
        """))

        # Employment
        conn.execute(text("""
            INSERT INTO EMPLOYMENT (
                EMPLOYMENTID, ALUMNIID, EMPLOYERNAME,
                INDUSTRY, POSITION, STARTYEAR, ENDYEAR
            )
            VALUES
            (1, 1001, 'Deloitte', 'Consulting',
                'Financial Analyst', 2018, 2021),
            (2, 1001, 'Bank of America', 'Banking',
                'Senior Analyst', 2021, NULL);
        """))

        # Membership
        conn.execute(text("""
            INSERT INTO ALUMNI_MEMBERSHIP (
                MEMBERID, ALUMNIID, ORGANIZATION, ROLE,
                STARTYEAR, ENDYEAR
            )
            VALUES (
                1, 1001,
                'Howard Alumni Network',
                'Member',
                2019, NULL
            );
        """))

        # Campaigns
        conn.execute(text("""
            INSERT INTO CAMPAIGN (CAMPAIGNID, CAMPAIGNNAME, GOALAMOUNT, STATUS)
            VALUES
            (1, 'Student Success Fund', 50000, 'Active'),
            (2, 'Campus Renovation Initiative', 200000, 'Active');
        """))

        # Initial contribution
        conn.execute(text("""
            INSERT INTO CONTRIBUTION (
                CONTRIBUTIONID, ALUMNIID, CAMPAIGNID,
                CONTRIBUTIONDATE, AMOUNT
            )
            VALUES (9001, 1001, 1, '2023-10-15', 250.00);
        """))


# -------------------------------------------------------------------
#  BASIC DATA ACCESS HELPERS
# -------------------------------------------------------------------
def get_alumni() -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM ALUMNI", engine)


def get_alumni_by_id(alumni_id: int) -> pd.DataFrame:
    sql = text("SELECT * FROM ALUMNI WHERE ALUMNIID = :aid")
    return pd.read_sql(sql, engine, params={"aid": alumni_id})


def get_degrees_for_alumni(alumni_id: int) -> pd.DataFrame:
    sql = text("SELECT * FROM DEGREE WHERE ALUMNIID = :aid")
    return pd.read_sql(sql, engine, params={"aid": alumni_id})


def get_employment_for_alumni(alumni_id: int) -> pd.DataFrame:
    sql = text("SELECT * FROM EMPLOYMENT WHERE ALUMNIID = :aid")
    return pd.read_sql(sql, engine, params={"aid": alumni_id})


def get_memberships_for_alumni(alumni_id: int) -> pd.DataFrame:
    sql = text("SELECT * FROM ALUMNI_MEMBERSHIP WHERE ALUMNIID = :aid")
    return pd.read_sql(sql, engine, params={"aid": alumni_id})


def get_contributions_for_alumni(alumni_id: int) -> pd.DataFrame:
    """
    Contributions for a single alumni, joined with campaign names.
    """
    sql = text("""
        SELECT
            c.CONTRIBUTIONID,
            c.CONTRIBUTIONDATE,
            c.AMOUNT,
            cp.CAMPAIGNNAME
        FROM CONTRIBUTION c
        LEFT JOIN CAMPAIGN cp
            ON c.CAMPAIGNID = cp.CAMPAIGNID
        WHERE c.ALUMNIID = :aid
        ORDER BY c.CONTRIBUTIONDATE DESC
    """)
    return pd.read_sql(sql, engine, params={"aid": alumni_id})


# -------------------------------------------------------------------
#  CAMPAIGNS + CONTRIBUTIONS (ADMIN / ALUMNI)
# -------------------------------------------------------------------
def get_campaigns() -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM CAMPAIGN", engine)


def create_contribution(alumni_id: int, campaign_id: int, amount: float, date_str: str):
    """Insert a new contribution record."""
    with engine.begin() as conn:
        next_id = conn.execute(
            text("SELECT COALESCE(MAX(CONTRIBUTIONID), 9000) + 1 FROM CONTRIBUTION")
        ).scalar()

        sql = text("""
            INSERT INTO CONTRIBUTION (
                CONTRIBUTIONID,
                ALUMNIID,
                CAMPAIGNID,
                CONTRIBUTIONDATE,
                AMOUNT
            )
            VALUES (
                :cid,
                :aid,
                :camp,
                :cdate,
                :amt
            )
        """)

        conn.execute(
            sql,
            {
                "cid": int(next_id),
                "aid": int(alumni_id),
                "camp": int(campaign_id),
                "cdate": date_str,
                "amt": float(amount),
            },
        )


def get_all_contributions() -> pd.DataFrame:
    """
    For the admin 'Contributions' drill-down:
    CONTRIBUTIONDATE | FIRSTNAME | LASTNAME | CAMPAIGNNAME | AMOUNT
    """
    sql = text("""
        SELECT
            c.CONTRIBUTIONDATE,
            a.FIRSTNAME,
            a.LASTNAME,
            cp.CAMPAIGNNAME,
            c.AMOUNT
        FROM CONTRIBUTION c
        LEFT JOIN ALUMNI a
            ON c.ALUMNIID = a.ALUMNIID
        LEFT JOIN CAMPAIGN cp
            ON c.CAMPAIGNID = cp.CAMPAIGNID
        ORDER BY c.CONTRIBUTIONDATE DESC
    """)
    return pd.read_sql(sql, engine)


def update_alumni_contact(alumni_id: int, email: str, phone: str, mailing_list: str):
    """Used by 'My Profile & Updates' form in alumni_app.py."""
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE ALUMNI
                SET PRIMARYEMAIL = :email,
                    PHONE        = :phone,
                    MAILING_LIST = :ml
                WHERE ALUMNIID = :aid
            """),
            {
                "email": email,
                "phone": phone,
                "ml": mailing_list,
                "aid": alumni_id,
            },
        )


# -------------------------------------------------------------------
#  DASHBOARD SUMMARY HELPERS
# -------------------------------------------------------------------
def get_summary_stats():
    """Aggregates used by the admin dashboard metrics."""
    with engine.begin() as conn:
        total_alumni = conn.execute(
            text("SELECT COUNT(*) FROM ALUMNI")
        ).scalar()

        total_employers = conn.execute(
            text("SELECT COUNT(DISTINCT EMPLOYERNAME) FROM EMPLOYMENT")
        ).scalar()

        active_campaigns = conn.execute(
            text("SELECT COUNT(*) FROM CAMPAIGN WHERE STATUS = 'Active'")
        ).scalar()

        total_contributions = conn.execute(
            text("SELECT COALESCE(SUM(AMOUNT), 0) FROM CONTRIBUTION")
        ).scalar()

    return {
        "total_alumni": total_alumni or 0,
        "total_employers": total_employers or 0,
        "total_campaigns": active_campaigns or 0,
        "total_contributions": total_contributions or 0.0,
    }


def get_employer_summary() -> pd.DataFrame:
    """
    Returns: EMPLOYERNAME | INDUSTRY | NUM_ALUMNI
    Uses pandas groupby so it works cleanly on SQLite.
    """
    emp_df = pd.read_sql("SELECT * FROM EMPLOYMENT", engine)

    if emp_df.empty:
        return pd.DataFrame(columns=["EMPLOYERNAME", "INDUSTRY", "NUM_ALUMNI"])

    grouped = (
        emp_df.groupby(["EMPLOYERNAME", "INDUSTRY"])["ALUMNIID"]
        .nunique()
        .reset_index(name="NUM_ALUMNI")
    )

    return grouped[["EMPLOYERNAME", "INDUSTRY", "NUM_ALUMNI"]]


# -------------------------------------------------------------------
#  Initialize DB when module is imported
# -------------------------------------------------------------------
init_db()
