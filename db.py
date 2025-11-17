import pandas as pd
from sqlalchemy import create_engine, text

# ========= DATABASE SETUP =========
engine = create_engine("sqlite:///alumni.db", echo=False)


# ========= INITIALIZE DB & SEED DATA =========
def init_db():
    """Create tables and insert demo records if they do not exist."""
    with engine.begin() as conn:
        # ALUMNI TABLE
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ALUMNI (
                ALUMNIID INTEGER PRIMARY KEY,
                FIRSTNAME TEXT,
                LASTNAME TEXT,
                PRIMARYEMAIL TEXT,
                PHONE TEXT,
                GRAD_MAJOR TEXT,
                ALUM_GRADYEAR INTEGER,
                MAILING_LIST TEXT,
                LINKEDIN TEXT
            );
        """))

        # DEGREES TABLE
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

        # EMPLOYMENT TABLE
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS EMPLOYMENT (
                EMPLOYMENTID INTEGER PRIMARY KEY,
                ALUMNIID INTEGER,
                COMPANY TEXT,
                POSITION TEXT,
                STARTYEAR INTEGER,
                ENDYEAR INTEGER
            );
        """))

        # MEMBERSHIPS TABLE
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS MEMBERSHIP (
                MEMBERSHIPID INTEGER PRIMARY KEY,
                ALUMNIID INTEGER,
                ASSOCIATION TEXT,
                ROLE TEXT
            );
        """))

        # CAMPAIGN TABLE
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS CAMPAIGN (
                CAMPAIGNID INTEGER PRIMARY KEY,
                CAMPAIGNNAME TEXT,
                GOALAMOUNT REAL
            );
        """))

        # CONTRIBUTIONS TABLE
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS CONTRIBUTION (
                CONTRIBUTIONID INTEGER PRIMARY KEY,
                ALUMNIID INTEGER,
                CAMPAIGNID INTEGER,
                CONTRIBUTIONDATE TEXT,
                AMOUNT REAL
            );
        """))

    seed_demo_data()


def seed_demo_data():
    """Insert demo data only if tables are empty."""
    with engine.begin() as conn:

        # Seed alumni
        count = conn.execute(text("SELECT COUNT(*) FROM ALUMNI")).scalar()
        if count == 0:
            conn.execute(text("""
                INSERT INTO ALUMNI VALUES
                (1001, 'Maya', 'Johnson', 'maya.johnson@email.com',
                 '202-555-1111', 'Finance', 2023, 'Yes',
                 'https://www.linkedin.com/in/examplemaya'),

                (1002, 'Tariq', 'Williams', 'tariq.w@alumni.howard.edu',
                 '202-555-2222', 'Marketing', 2022, 'No',
                 'https://www.linkedin.com/in/exampletariq')
            """))

        # Seed degrees
        count = conn.execute(text("SELECT COUNT(*) FROM DEGREE")).scalar()
        if count == 0:
            conn.execute(text("""
                INSERT INTO DEGREE VALUES
                (1, 1001, 'Finance', 'Economics', 'School of Business', 'Cum Laude', 'May', 2023),
                (2, 1002, 'Marketing', NULL, 'School of Business', NULL, 'May', 2022)
            """))

        # Seed employment
        count = conn.execute(text("SELECT COUNT(*) FROM EMPLOYMENT")).scalar()
        if count == 0:
            conn.execute(text("""
                INSERT INTO EMPLOYMENT VALUES
                (1, 1001, 'Goldman Sachs', 'Analyst', 2023, NULL),
                (2, 1002, 'Nike', 'Marketing Coordinator', 2022, NULL)
            """))

        # Seed memberships
        count = conn.execute(text("SELECT COUNT(*) FROM MEMBERSHIP")).scalar()
        if count == 0:
            conn.execute(text("""
                INSERT INTO MEMBERSHIP VALUES
                (1, 1001, 'HU Alumni Association', 'Member'),
                (2, 1002, 'HU Young Professionals', 'Officer')
            """))

        # Seed campaigns
        count = conn.execute(text("SELECT COUNT(*) FROM CAMPAIGN")).scalar()
        if count == 0:
            conn.execute(text("""
                INSERT INTO CAMPAIGN VALUES
                (5001, 'Business School Fundraiser', 25000),
                (5002, 'Dean’s Leadership Circle', 50000)
            """))

        # Seed contributions
        count = conn.execute(text("SELECT COUNT(*) FROM CONTRIBUTION")).scalar()
        if count == 0:
            conn.execute(text("""
                INSERT INTO CONTRIBUTION VALUES
                (9001, 1001, 5001, '2024-01-10', 250.00),
                (9002, 1002, 5002, '2024-02-14', 500.00)
            """))


# ========= GETTERS (USED BY STREAMLIT APP) =========
def get_alumni():
    return pd.read_sql("SELECT * FROM ALUMNI", engine)


def get_alumni_by_id(aid: int):
    return pd.read_sql(f"SELECT * FROM ALUMNI WHERE ALUMNIID = {aid}", engine)


def get_degrees_for_alumni(aid: int):
    return pd.read_sql(f"SELECT * FROM DEGREE WHERE ALUMNIID = {aid}", engine)


def get_employment_for_alumni(aid: int):
    return pd.read_sql(f"SELECT * FROM EMPLOYMENT WHERE ALUMNIID = {aid}", engine)


def get_memberships_for_alumni(aid: int):
    return pd.read_sql(f"SELECT * FROM MEMBERSHIP WHERE ALUMNIID = {aid}", engine)


def get_contributions_for_alumni(aid: int):
    return pd.read_sql(f"SELECT * FROM CONTRIBUTION WHERE ALUMNIID = {aid}", engine)


def get_campaigns():
    return pd.read_sql("SELECT * FROM CAMPAIGN", engine)


def get_all_contributions():
    sql = """
        SELECT c.CONTRIBUTIONDATE, c.AMOUNT,
               a.FIRSTNAME, a.LASTNAME,
               x.CAMPAIGNNAME
        FROM CONTRIBUTION c
        JOIN ALUMNI a ON a.ALUMNIID = c.ALUMNIID
        JOIN CAMPAIGN x ON x.CAMPAIGNID = c.CAMPAIGNID
        ORDER BY c.CONTRIBUTIONDATE DESC
    """
    return pd.read_sql(sql, engine)


def get_employer_summary():
    sql = """
        SELECT COMPANY, COUNT(*) AS NUM_ALUMNI
        FROM EMPLOYMENT
        GROUP BY COMPANY
        ORDER BY NUM_ALUMNI DESC
    """
    return pd.read_sql(sql, engine)


def get_summary_stats():
    with engine.begin() as conn:
        return {
            "total_alumni": conn.execute(text("SELECT COUNT(*) FROM ALUMNI")).scalar(),
            "total_employers": conn.execute(text("SELECT COUNT(DISTINCT COMPANY) FROM EMPLOYMENT")).scalar(),
            "total_campaigns": conn.execute(text("SELECT COUNT(*) FROM CAMPAIGN")).scalar(),
            "total_contributions": conn.execute(text("SELECT COALESCE(SUM(AMOUNT),0) FROM CONTRIBUTION")).scalar(),
        }


# ========= UPDATE FUNCTIONS =========
def update_alumni_contact(aid: int, email: str, phone: str, mailing: str):
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE ALUMNI
                SET PRIMARYEMAIL = :email,
                    PHONE = :phone,
                    MAILING_LIST = :mailing
                WHERE ALUMNIID = :aid
            """),
            {"email": email, "phone": phone, "mailing": mailing, "aid": aid},
        )


# ========= CONTRIBUTION INSERT =========
def create_contribution(alumni_id: int, campaign_id: int, amount: float, date_str: str):
    with engine.begin() as conn:
        next_id = conn.execute(
            text("SELECT COALESCE(MAX(CONTRIBUTIONID), 9000) + 1 FROM CONTRIBUTION")
        ).scalar()

        conn.execute(
            text("""
                INSERT INTO CONTRIBUTION (
                    CONTRIBUTIONID,
                    ALUMNIID,
                    CAMPAIGNID,
                    CONTRIBUTIONDATE,
                    AMOUNT
                )
                VALUES (:cid, :aid, :camp, :cdate, :amt)
            """),
            {
                "cid": int(next_id),
                "aid": int(alumni_id),
                "camp": int(campaign_id),
                "cdate": date_str,
                "amt": float(amount),
            },
        )
