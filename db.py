import pandas as pd
from sqlalchemy import create_engine, text

# -------------------------------------------------------------------
# SQLite Engine
# -------------------------------------------------------------------
engine = create_engine("sqlite:///alumni.db", echo=False, future=True)


# -------------------------------------------------------------------
#  CREATE TABLES + SEED DEMO DATA
# -------------------------------------------------------------------
def init_db():
    """Create all tables and insert demo records only if tables are empty."""

    with engine.begin() as conn:
        # --------------------------
        # ALUMNI TABLE
        # --------------------------
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ALUMNI (
                ALUMNIID INTEGER PRIMARY KEY,
                FIRSTNAME TEXT,
                LASTNAME TEXT,
                EMAIL TEXT,
                PHONE TEXT,
                MAJOR TEXT,
                GRADYEAR INTEGER,
                MAILING_LIST TEXT,
                LINKEDIN TEXT
            );
        """))

        # --------------------------
        # DEGREE TABLE
        # --------------------------
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS DEGREE (
                DEGREEID INTEGER PRIMARY KEY,
                ALUMNIID INTEGER,
                MAJOR TEXT,
                MINOR TEXT,
                SCHOOL TEXT,
                HONORS TEXT,
                GRADMONTH TEXT,
                GRADYEAR INTEGER
            );
        """))

        # --------------------------
        # EMPLOYMENT TABLE
        # --------------------------
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS EMPLOYMENT (
                EMPLOYMENTID INTEGER PRIMARY KEY,
                ALUMNIID INTEGER,
                EMPLOYERNAME TEXT,
                INDUSTRY TEXT,
                POSITION TEXT,
                STARTYEAR INTEGER,
                ENDYEAR INTEGER
            );
        """))

        # --------------------------
        # ALUMNI MEMBERSHIP TABLE
        # --------------------------
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ALUMNI_MEMBERSHIP (
                MEMBERID INTEGER PRIMARY KEY,
                ALUMNIID INTEGER,
                ORGANIZATION TEXT,
                ROLE TEXT,
                STARTYEAR INTEGER,
                ENDYEAR INTEGER
            );
        """))

        # --------------------------
        # CAMPAIGN TABLE
        # --------------------------
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS CAMPAIGN (
                CAMPAIGNID INTEGER PRIMARY KEY,
                CAMPAIGNNAME TEXT,
                GOALAMOUNT FLOAT,
                STATUS TEXT
            );
        """))

        # --------------------------
        # CONTRIBUTION TABLE
        # --------------------------
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS CONTRIBUTION (
                CONTRIBUTIONID INTEGER PRIMARY KEY,
                ALUMNIID INTEGER,
                CAMPAIGNID INTEGER,
                CONTRIBUTIONDATE TEXT,
                AMOUNT FLOAT
            );
        """))

    seed_demo_data()
    ensure_linkedin_column()


# -------------------------------------------------------------------
#  ADD LINKEDIN COLUMN IF NOT EXISTS
# -------------------------------------------------------------------
def ensure_linkedin_column():
    """Ensures LinkedIn column exists and seeds a demo link."""
    with engine.begin() as conn:
        cols = conn.execute(text("PRAGMA table_info(ALUMNI);")).fetchall()
        col_names = [c[1] for c in cols]

        if "LINKEDIN" not in col_names:
            conn.execute(text("ALTER TABLE ALUMNI ADD COLUMN LINKEDIN TEXT;"))

        # Add LinkedIn link for demo profile (Maya Johnson = ALUMNIID 1001)
        conn.execute(text("""
            UPDATE ALUMNI
            SET LINKEDIN = 'https://www.linkedin.com/in/maya-johnson-demo'
            WHERE ALUMNIID = 1001 AND (LINKEDIN IS NULL OR LINKEDIN = '');
        """))


# -------------------------------------------------------------------
#  SEED DEMO DATA
# -------------------------------------------------------------------
def seed_demo_data():
    with engine.begin() as conn:
        # Check if already seeded
        count = conn.execute(text("SELECT COUNT(*) FROM ALUMNI")).scalar()
        if count > 0:
            return

        # Insert demo alumni
        conn.execute(text("""
            INSERT INTO ALUMNI (ALUMNIID, FIRSTNAME, LASTNAME, EMAIL, PHONE,
                MAJOR, GRADYEAR, MAILING_LIST, LINKEDIN)
            VALUES
            (1001, 'Maya', 'Johnson', 'maya.johnson@email.com',
             '202-555-7821', 'Finance', 2018, 'Yes', '');
        """))

        # Degree
        conn.execute(text("""
            INSERT INTO DEGREE (DEGREEID, ALUMNIID, MAJOR, MINOR, SCHOOL,
                HONORS, GRADMONTH, GRADYEAR)
            VALUES (1, 1001, 'Finance', 'None',
                'Howard University School of Business', 'Cum Laude', 'May', 2018);
        """))

        # Employment
        conn.execute(text("""
            INSERT INTO EMPLOYMENT (EMPLOYMENTID, ALUMNIID, EMPLOYERNAME,
                INDUSTRY, POSITION, STARTYEAR, ENDYEAR)
            VALUES
            (1, 1001, 'Deloitte', 'Consulting', 'Financial Analyst', 2018, 2021),
            (2, 1001, 'Bank of America', 'Banking', 'Senior Analyst', 2021, NULL);
        """))

        # Membership
        conn.execute(text("""
            INSERT INTO ALUMNI_MEMBERSHIP (MEMBERID, ALUMNIID, ORGANIZATION,
                ROLE, STARTYEAR, ENDYEAR)
            VALUES (1, 1001, 'Howard Alumni Network', 'Member', 2019, NULL);
        """))

        # Campaigns
        conn.execute(text("""
            INSERT INTO CAMPAIGN (CAMPAIGNID, CAMPAIGNNAME, GOALAMOUNT, STATUS)
            VALUES
            (1, 'Student Success Fund', 50000, 'Active'),
            (2, 'Campus Renovation Initiative', 200000, 'Active');
        """))

        # Contributions
        conn.execute(text("""
            INSERT INTO CONTRIBUTION (CONTRIBUTIONID, ALUMNIID, CAMPAIGNID,
                CONTRIBUTIONDATE, AMOUNT)
            VALUES
            (9001, 1001, 1, '2023-10-15', 250.00);
        """))


# -------------------------------------------------------------------
#  ALUMNI QUERIES
# -------------------------------------------------------------------
def get_alumni():
    return pd.read_sql("SELECT * FROM ALUMNI", engine)


def get_alumni_by_id(alumni_id: int):
    sql = text("SELECT * FROM ALUMNI WHERE ALUMNIID = :aid")
    return pd.read_sql(sql, engine, params={"aid": alumni_id})


def get_degrees_for_alumni(alumni_id: int):
    sql = text("SELECT * FROM DEGREE WHERE ALUMNIID = :aid")
    return pd.read_sql(sql, engine, params={"aid": alumni_id})


def get_employment_for_alumni(alumni_id: int):
    sql = text("SELECT * FROM EMPLOYMENT WHERE ALUMNIID = :aid")
    return pd.read_sql(sql, engine, params={"aid": alumni_id})


def get_memberships_for_alumni(alumni_id: int):
    sql = text("SELECT * FROM ALUMNI_MEMBERSHIP WHERE ALUMNIID = :aid")
    return pd.read_sql(sql, engine, params={"aid": alumni_id})


# -------------------------------------------------------------------
#  CAMPAIGN + CONTRIBUTION QUERIES
# -------------------------------------------------------------------
def get_campaigns():
    return pd.read_sql("SELECT * FROM CAMPAIGN", engine)


def get_contributions():
    return pd.read_sql("SELECT * FROM CONTRIBUTION", engine)


def create_contribution(alumni_id: int, campaign_id: int, amount: float, date_str: str):
    with engine.begin() as conn:
        next_id = conn.execute(
            text("SELECT COALESCE(MAX(CONTRIBUTIONID), 9000) + 1 FROM CONTRIBUTION")
        ).scalar()

        sql = text("""
            INSERT INTO CONTRIBUTION (
                CONTRIBUTIONID, ALUMNIID, CAMPAIGNID, CONTRIBUTIONDATE, AMOUNT
            )
            VALUES (:cid, :aid, :camp, :cdate, :amt)
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


# -------------------------------------------------------------------
#  DASHBOARD SUMMARY FUNCTIONS
# -------------------------------------------------------------------
def get_summary_stats():
    with engine.begin() as conn:
        total_alumni = conn.execute(text("SELECT COUNT(*) FROM ALUMNI")).scalar()
        total_employers = conn.execute(text("SELECT COUNT(DISTINCT EMPLOYERNAME) FROM EMPLOYMENT")).scalar()
        active_campaigns = conn.execute(text("SELECT COUNT(*) FROM CAMPAIGN WHERE STATUS = 'Active'")).scalar()
        total_contributions = conn.execute(text("SELECT SUM(AMOUNT) FROM CONTRIBUTION")).scalar()

    return {
        "total_alumni": total_alumni,
        "total_employers": total_employers,
        "active_campaigns": active_campaigns,
        "total_contributions": total_contributions or 0,
    }


# -------------------------------------------------------------------
#  EMPLOYER SUMMARY (FIXED)
# -------------------------------------------------------------------
def get_employer_summary() -> pd.DataFrame:
    """
    Returns: EMPLOYERNAME | INDUSTRY | NUM_ALUMNI
    Safe for SQLite — no joins, no schema issues.
    """
    df = pd.read_sql("SELECT * FROM EMPLOYMENT", engine)

    if df.empty:
        return pd.DataFrame(columns=["EMPLOYERNAME", "INDUSTRY", "NUM_ALUMNI"])

    cols = df.columns

    name_col = "EMPLOYERNAME" if "EMPLOYERNAME" in cols else "EMPLOYER"
    alum_col = "ALUMNIID" if "ALUMNIID" in cols else cols[0]

    if "INDUSTRY" in cols:
        grouped = (
            df.groupby([name_col, "INDUSTRY"])[alum_col]
              .nunique()
              .reset_index(name="NUM_ALUMNI")
        )
    else:
        grouped = (
            df.groupby([name_col])[alum_col]
              .nunique()
              .reset_index(name="NUM_ALUMNI")
        )
        grouped["INDUSTRY"] = ""

    if name_col != "EMPLOYERNAME":
        grouped.rename(columns={name_col: "EMPLOYERNAME"}, inplace=True)

    return grouped[["EMPLOYERNAME", "INDUSTRY", "NUM_ALUMNI"]]

# -------------------------------------------------------------------
# Initialize DB on import
# -------------------------------------------------------------------
init_db()
