from sqlalchemy import create_engine, text
import pandas as pd
import os

# --------------------------------------------------
# Database setup
# --------------------------------------------------
DB_URL = os.getenv("ALUMNI_DB_URL", "sqlite:///alumni.db")
engine = create_engine(DB_URL, echo=False, future=True)


# --------------------------------------------------
# LinkedIn helper: add column + demo data
# --------------------------------------------------
def ensure_linkedin_column_and_demo_data() -> None:
    """
    Make sure ALUMNI has a LINKEDIN column and a demo URL for Maya (ALUMNIID 1001).
    Safe to call multiple times.
    """
    with engine.begin() as conn:
        # 1. Check existing columns
        cols = conn.execute(text("PRAGMA table_info(ALUMNI);")).fetchall()
        col_names = [c[1] for c in cols]

        # 2. If LINKEDIN column doesn't exist yet, add it
        if "LINKEDIN" not in col_names:
            conn.execute(text("ALTER TABLE ALUMNI ADD COLUMN LINKEDIN TEXT;"))

        # 3. Give Maya Johnson (1001) a demo LinkedIn URL if blank
        conn.execute(
            text(
                """
                UPDATE ALUMNI
                SET LINKEDIN = :url
                WHERE ALUMNIID = 1001
                  AND (LINKEDIN IS NULL OR LINKEDIN = '')
                """
            ),
            {"url": "https://www.linkedin.com/in/maya-johnson-demo"},
        )


# --------------------------------------------------
# Create tables + seed data
# --------------------------------------------------
def init_db() -> None:
    """Create tables and insert demo records if they do not exist."""
    with engine.begin() as conn:
        # ---------- ALUMNI ----------
        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS ALUMNI (
                ALUMNIID      INTEGER PRIMARY KEY,
                FIRSTNAME     TEXT NOT NULL,
                LASTNAME      TEXT NOT NULL,
                PRIMARYEMAIL  TEXT NOT NULL,
                PHONE         TEXT NOT NULL,
                ALUM_GRADYEAR INTEGER NOT NULL,
                GRAD_MAJOR    TEXT NOT NULL,
                MAILING_LIST  TEXT NOT NULL
            );
            """
        )

        # ---------- DEGREE ----------
        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS DEGREE (
                DEGREEID   INTEGER PRIMARY KEY,
                ALUMNIID   INTEGER NOT NULL,
                MAJOR      TEXT NOT NULL,
                MINOR      TEXT,
                SCHOOL     TEXT NOT NULL,
                HONORS     TEXT,
                GRADMONTH  TEXT NOT NULL,
                GRADYEAR   INTEGER NOT NULL,
                FOREIGN KEY (ALUMNIID) REFERENCES ALUMNI(ALUMNIID)
            );
            """
        )

        # ---------- EMPLOYMENT ----------
        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS EMPLOYMENT (
                EMPLOYMENTID   INTEGER PRIMARY KEY,
                ALUMNIID       INTEGER NOT NULL,
                EMPLOYERNAME   TEXT NOT NULL,
                POSITIONTITLE  TEXT NOT NULL,
                CITY           TEXT,
                STATE          TEXT,
                STARTYEAR      INTEGER,
                ENDYEAR        INTEGER,
                FOREIGN KEY (ALUMNIID) REFERENCES ALUMNI(ALUMNIID)
            );
            """
        )

        # ---------- MEMBERSHIP ----------
        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS ALUMNI_MEMBERSHIP (
                MEMBERSHIPID INTEGER PRIMARY KEY,
                ALUMNIID     INTEGER NOT NULL,
                ORGNAME      TEXT NOT NULL,
                ROLE         TEXT,
                STARTYEAR    INTEGER,
                ENDYEAR      INTEGER,
                FOREIGN KEY (ALUMNIID) REFERENCES ALUMNI(ALUMNIID)
            );
            """
        )

        # ---------- CAMPAIGN ----------
        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS CAMPAIGN (
                CAMPAIGNID   INTEGER PRIMARY KEY,
                CAMPAIGNNAME TEXT NOT NULL,
                GOALAMOUNT   REAL NOT NULL
            );
            """
        )

        # ---------- CONTRIBUTION ----------
        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS CONTRIBUTION (
                CONTRIBUTIONID   INTEGER PRIMARY KEY,
                ALUMNIID         INTEGER NOT NULL,
                CAMPAIGNID       INTEGER NOT NULL,
                CONTRIBUTIONDATE TEXT NOT NULL,
                AMOUNT           REAL NOT NULL,
                FOREIGN KEY (ALUMNIID)   REFERENCES ALUMNI(ALUMNIID),
                FOREIGN KEY (CAMPAIGNID) REFERENCES CAMPAIGN(CAMPAIGNID)
            );
            """
        )

        # ---------- SEED DATA (only if ALUMNI empty) ----------
        count = conn.execute(text("SELECT COUNT(*) FROM ALUMNI")).scalar()
        if count == 0:
            # Seed ALUMNI
            conn.exec_driver_sql(
                """
                INSERT INTO ALUMNI (
                    ALUMNIID, FIRSTNAME, LASTNAME,
                    PRIMARYEMAIL, PHONE, ALUM_GRADYEAR,
                    GRAD_MAJOR, MAILING_LIST
                )
                VALUES
                    (1001, 'Maya',   'Johnson',  'maya.johnson@email.com',  '202-555-7821', 2018, 'Finance',          'Yes'),
                    (1002, 'Jordan', 'Smith',    'jordan.smith@email.com',  '404-555-6719', 2019, 'Marketing',        'Yes'),
                    (1003, 'Amira',  'Patel',    'amira.patel@email.com',   '312-555-2190', 2020, 'Computer Information Systems', 'Yes'),
                    (1004, 'Isaiah', 'Thompson', 'isaiah.thompson@email.com','443-555-9898', 2017, 'Finance',          'No'),
                    (1005, 'Nia',    'Brown',    'nia.brown@email.com',     '703-555-3104', 2021, 'Supply Chain',     'Yes');
                """
            )

            # Seed DEGREE
            conn.exec_driver_sql(
                """
                INSERT INTO DEGREE (
                    DEGREEID, ALUMNIID, MAJOR, MINOR,
                    SCHOOL, HONORS, GRADMONTH, GRADYEAR
                )
                VALUES
                    (2001, 1001, 'Finance',                     'None', 'Howard University School of Business', 'Cum Laude', 'May', 2018),
                    (2002, 1002, 'Marketing',                   'None', 'Howard University School of Business', NULL,       'May', 2019),
                    (2003, 1003, 'Computer Information Systems','Math', 'Howard University School of Business', 'Magna Cum Laude', 'May', 2020),
                    (2004, 1004, 'Finance',                     'Economics','Howard University School of Business', NULL,   'May', 2017),
                    (2005, 1005, 'Supply Chain',                'None', 'Howard University School of Business', NULL,       'May', 2021);
                """
            )

            # Seed EMPLOYMENT
            conn.exec_driver_sql(
                """
                INSERT INTO EMPLOYMENT (
                    EMPLOYMENTID, ALUMNIID, EMPLOYERNAME,
                    POSITIONTITLE, CITY, STATE, STARTYEAR, ENDYEAR
                )
                VALUES
                    (3001, 1001, 'JPMorgan Chase',  'Financial Analyst',        'New York',      'NY', 2018, NULL),
                    (3002, 1002, 'Procter & Gamble','Brand Manager',            'Cincinnati',    'OH', 2019, NULL),
                    (3003, 1003, 'Deloitte',        'Technology Consultant',    'Chicago',       'IL', 2020, NULL),
                    (3004, 1004, 'Goldman Sachs',   'Investment Banking Assoc', 'Baltimore',     'MD', 2017, 2021),
                    (3005, 1005, 'Amazon',          'Operations Manager',       'Arlington',     'VA', 2021, NULL);
                """
            )

            # Seed MEMBERSHIP
            conn.exec_driver_sql(
                """
                INSERT INTO ALUMNI_MEMBERSHIP (
                    MEMBERSHIPID, ALUMNIID, ORGNAME, ROLE, STARTYEAR, ENDYEAR
                )
                VALUES
                    (4001, 1001, 'HU Alumni Association – DC Chapter', 'Treasurer',    2019, NULL),
                    (4002, 1002, 'HU Alumni Association – Atlanta',    'Member',       2020, NULL),
                    (4003, 1003, 'HU Tech Alumni Network',             'Mentor',       2021, NULL),
                    (4004, 1004, 'HU Finance Alumni Circle',           'Member',       2018, 2022),
                    (4005, 1005, 'HU Supply Chain Alumni Group',       'Member',       2022, NULL);
                """
            )

            # Seed CAMPAIGN
            conn.exec_driver_sql(
                """
                INSERT INTO CAMPAIGN (CAMPAIGNID, CAMPAIGNNAME, GOALAMOUNT)
                VALUES
                    (5001, 'School of Business Scholarship Fund', 50000.0),
                    (5002, 'Center for Financial Excellence Lab Upgrade', 75000.0);
                """
            )

            # Seed CONTRIBUTION
            conn.exec_driver_sql(
                """
                INSERT INTO CONTRIBUTION (
                    CONTRIBUTIONID, ALUMNIID, CAMPAIGNID,
                    CONTRIBUTIONDATE, AMOUNT
                )
                VALUES
                    (9001, 1001, 5001, '2024-01-15', 2500.00),
                    (9002, 1002, 5001, '2024-02-10', 1500.00),
                    (9003, 1003, 5002, '2024-03-05', 3500.00),
                    (9004, 1004, 5002, '2024-04-20', 1000.00),
                    (9005, 1005, 5001, '2024-05-01',  500.00);
                """
            )

    # After tables + seed are ready, ensure LinkedIn column/demo link
    ensure_linkedin_column_and_demo_data()


# --------------------------------------------------
# Data access helpers used by Streamlit app
# --------------------------------------------------
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
    sql = text(
        """
        SELECT c.CONTRIBUTIONID,
               c.CONTRIBUTIONDATE,
               c.AMOUNT,
               p.CAMPAIGNNAME
        FROM CONTRIBUTION c
        JOIN CAMPAIGN p ON c.CAMPAIGNID = p.CAMPAIGNID
        WHERE c.ALUMNIID = :aid
        ORDER BY c.CONTRIBUTIONDATE DESC
        """
    )
    return pd.read_sql(sql, engine, params={"aid": alumni_id})


def get_campaigns() -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM CAMPAIGN", engine)


def create_contribution(
    alumni_id: int, campaign_id: int, amount: float, date_str: str
) -> None:
    """Insert a new contribution record."""
    with engine.begin() as conn:
        next_id = conn.execute(
            text("SELECT COALESCE(MAX(CONTRIBUTIONID), 9000) + 1 AS nid FROM CONTRIBUTION")
        ).scalar()

        sql = text(
            """
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
            """
        )
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


def get_summary_stats() -> dict:
    """Basic counts for the admin dashboard."""
    with engine.begin() as conn:
        total_alumni = conn.execute(text("SELECT COUNT(*) FROM ALUMNI")).scalar() or 0
        total_employers = (
            conn.execute(
                text("SELECT COUNT(DISTINCT EMPLOYERNAME) FROM EMPLOYMENT")
            ).scalar()
            or 0
        )
        total_campaigns = conn.execute(text("SELECT COUNT(*) FROM CAMPAIGN")).scalar() or 0
        total_contributions = (
            conn.execute(text("SELECT COALESCE(SUM(AMOUNT), 0) FROM CONTRIBUTION")).scalar()
            or 0.0
        )

    return {
        "total_alumni": int(total_alumni),
        "total_employers": int(total_employers),
        "total_campaigns": int(total_campaigns),
        "total_contributions": float(total_contributions),
    }


def get_employer_summary() -> pd.DataFrame:
    """
    Employer drill-down for the admin dashboard:
    how many alumni per employer.
    """
    sql = text(
        """
        SELECT
            EMPLOYERNAME,
            COUNT(*) AS NUM_ALUMNI
        FROM EMPLOYMENT
        GROUP BY EMPLOYERNAME
        ORDER BY NUM_ALUMNI DESC, EMPLOYERNAME
        """
    )
    return pd.read_sql(sql, engine)


def get_all_contributions() -> pd.DataFrame:
    """
    All contributions joined with alumni & campaign names,
    used in the admin dashboard drill-down.
    """
    sql = text(
        """
        SELECT
            c.CONTRIBUTIONDATE,
            a.FIRSTNAME,
            a.LASTNAME,
            p.CAMPAIGNNAME,
            c.AMOUNT
        FROM CONTRIBUTION c
        JOIN ALUMNI   a ON c.ALUMNIID   = a.ALUMNIID
        JOIN CAMPAIGN p ON c.CAMPAIGNID = p.CAMPAIGNID
        ORDER BY c.CONTRIBUTIONDATE DESC, a.LASTNAME, a.FIRSTNAME
        """
    )
    return pd.read_sql(sql, engine)


def update_alumni_contact(alumni_id: int, email: str, phone: str, mailing_list: str) -> None:
    """Update email, phone, and mailing list flag for an alumni."""
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE ALUMNI
                SET PRIMARYEMAIL = :email,
                    PHONE        = :phone,
                    MAILING_LIST = :ml
                WHERE ALUMNIID  = :aid
                """
            ),
            {
                "email": email,
                "phone": phone,
                "ml": mailing_list,
                "aid": int(alumni_id),
            },
        )
