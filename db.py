from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

# -------------------------------------------------
# Database setup
# -------------------------------------------------

DB_PATH = Path("alumni.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)


# -------------------------------------------------
# Schema + seed data
# -------------------------------------------------

def init_db() -> None:
    """Create tables and insert demo records if they do not exist."""
    with engine.begin() as conn:
        # ALUMNI
        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS ALUMNI (
                ALUMNIID      INTEGER PRIMARY KEY,
                FIRSTNAME     TEXT NOT NULL,
                LASTNAME      TEXT NOT NULL,
                PRIMARYEMAIL  TEXT NOT NULL,
                PHONE         TEXT,
                GRAD_MAJOR    TEXT,
                ALUM_GRADYEAR INTEGER,
                MAILING_LIST  TEXT DEFAULT 'Yes',
                LINKEDIN      TEXT
            )
            """
        )

        # DEGREE
        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS DEGREE (
                DEGREEID  INTEGER PRIMARY KEY,
                ALUMNIID  INTEGER NOT NULL,
                MAJOR     TEXT,
                MINOR     TEXT,
                SCHOOL    TEXT,
                HONORS    TEXT,
                GRADMONTH TEXT,
                GRADYEAR  INTEGER,
                FOREIGN KEY (ALUMNIID) REFERENCES ALUMNI(ALUMNIID)
            )
            """
        )

        # EMPLOYMENT
        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS EMPLOYMENT (
                EMPLOYMENTID INTEGER PRIMARY KEY,
                ALUMNIID     INTEGER NOT NULL,
                EMPLOYERNAME TEXT,
                TITLE        TEXT,
                INDUSTRY     TEXT,
                CITY         TEXT,
                STATE        TEXT,
                STARTYEAR    INTEGER,
                FOREIGN KEY (ALUMNIID) REFERENCES ALUMNI(ALUMNIID)
            )
            """
        )

        # ALUMNI_MEMBERSHIP
        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS ALUMNI_MEMBERSHIP (
                MEMBERSHIPID INTEGER PRIMARY KEY,
                ALUMNIID     INTEGER NOT NULL,
                ORGNAME      TEXT,
                ROLE         TEXT,
                STARTYEAR    INTEGER,
                ENDYEAR      INTEGER,
                FOREIGN KEY (ALUMNIID) REFERENCES ALUMNI(ALUMNIID)
            )
            """
        )

        # CAMPAIGN
        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS CAMPAIGN (
                CAMPAIGNID   INTEGER PRIMARY KEY,
                CAMPAIGNNAME TEXT NOT NULL,
                GOALAMOUNT   REAL NOT NULL,
                STATUS       TEXT NOT NULL
            )
            """
        )

        # CONTRIBUTION
        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS CONTRIBUTION (
                CONTRIBUTIONID   INTEGER PRIMARY KEY,
                ALUMNIID         INTEGER NOT NULL,
                CAMPAIGNID       INTEGER NOT NULL,
                CONTRIBUTIONDATE TEXT NOT NULL,
                AMOUNT           REAL NOT NULL,
                FOREIGN KEY (ALUMNIID)  REFERENCES ALUMNI(ALUMNIID),
                FOREIGN KEY (CAMPAIGNID) REFERENCES CAMPAIGN(CAMPAIGNID)
            )
            """
        )

    # After schema is in place, seed data if needed
    seed_demo_data()
    ensure_linkedin_demo()


def seed_demo_data() -> None:
    """Insert a small set of demo rows if the tables are empty."""
    with engine.begin() as conn:
        # Only seed ALUMNI once
        count = conn.execute(text("SELECT COUNT(*) FROM ALUMNI")).scalar() or 0
        if count > 0:
            return

        # Alumni
        conn.exec_driver_sql(
            """
            INSERT INTO ALUMNI (ALUMNIID, FIRSTNAME, LASTNAME, PRIMARYEMAIL, PHONE, GRAD_MAJOR, ALUM_GRADYEAR, MAILING_LIST)
            VALUES
                (1001, 'Maya',  'Johnson', 'maya.johnson@email.com', '202-555-7821', 'Finance',        2018, 'Yes'),
                (1002, 'Jordan','Smith',   'jordan.smith@email.com','404-555-6719', 'Marketing',      2019, 'Yes'),
                (1003, 'Amira', 'Patel',   'amira.patel@email.com', '312-555-2190', 'Computer Info Systems', 2020, 'No'),
                (1004, 'Isaiah','Thompson','isaiah.thompson@email.com','443-555-9898','Finance',      2017, 'Yes'),
                (1005, 'Nia',   'Brown',   'nia.brown@email.com',   '703-555-3104', 'Supply Chain',  2021, 'Yes')
            """
        )

        # Degrees (one per alumni for demo)
        conn.exec_driver_sql(
            """
            INSERT INTO DEGREE (DEGREEID, ALUMNIID, MAJOR, MINOR, SCHOOL, HONORS, GRADMONTH, GRADYEAR)
            VALUES
                (2001, 1001, 'Finance',        'None', 'Howard University School of Business', 'Cum Laude', 'May', 2018),
                (2002, 1002, 'Marketing',      'None', 'Howard University School of Business', NULL,       'May', 2019),
                (2003, 1003, 'Computer Info Systems','Math','Howard University School of Business','Magna Cum Laude','May',2020),
                (2004, 1004, 'Finance',        'Accounting','Howard University School of Business',NULL,'May',2017),
                (2005, 1005, 'Supply Chain',   'None', 'Howard University School of Business', NULL,       'May', 2021)
            """
        )

        # Employment
        conn.exec_driver_sql(
            """
            INSERT INTO EMPLOYMENT (EMPLOYMENTID, ALUMNIID, EMPLOYERNAME, TITLE, INDUSTRY, CITY, STATE, STARTYEAR)
            VALUES
                (3001, 1001, 'Deloitte',            'Consultant',     'Consulting', 'Washington', 'DC', 2018),
                (3002, 1002, 'Procter & Gamble',    'Brand Manager',  'CPG',        'Cincinnati', 'OH', 2019),
                (3003, 1003, 'Google',              'Analyst',        'Technology', 'Mountain View', 'CA', 2020),
                (3004, 1004, 'Bank of America',     'Risk Analyst',   'Financial Services','Charlotte','NC',2017),
                (3005, 1005, 'Amazon',              'Operations Mgr', 'E-commerce', 'Seattle', 'WA', 2021)
            """
        )

        # Memberships
        conn.exec_driver_sql(
            """
            INSERT INTO ALUMNI_MEMBERSHIP (MEMBERSHIPID, ALUMNIID, ORGNAME, ROLE, STARTYEAR, ENDYEAR)
            VALUES
                (4001, 1001, 'HU Finance Alumni Network', 'Mentor', 2020, NULL),
                (4002, 1003, 'Tech Alumni Council',       'Member', 2021, NULL)
            """
        )

        # Campaigns
        conn.exec_driver_sql(
            """
            INSERT INTO CAMPAIGN (CAMPAIGNID, CAMPAIGNNAME, GOALAMOUNT, STATUS)
            VALUES
                (5001, 'Student Scholarship Fund', 50000, 'Active'),
                (5002, 'Study Abroad Support',    30000, 'Active')
            """
        )

        # Contributions
        conn.exec_driver_sql(
            """
            INSERT INTO CONTRIBUTION (CONTRIBUTIONID, ALUMNIID, CAMPAIGNID, CONTRIBUTIONDATE, AMOUNT)
            VALUES
                (9001, 1001, 5001, '2024-01-15', 1500.00),
                (9002, 1002, 5001, '2024-03-10',  750.00),
                (9003, 1003, 5002, '2024-05-01', 1000.00)
            """
        )


def ensure_linkedin_demo() -> None:
    """Ensure Maya has a demo LinkedIn URL; safe to run multiple times."""
    with engine.begin() as conn:
        try:
            conn.exec_driver_sql(
                """
                UPDATE ALUMNI
                SET LINKEDIN = 'https://www.linkedin.com/in/maya-johnson-demo'
                WHERE ALUMNIID = 1001
                  AND (LINKEDIN IS NULL OR LINKEDIN = '')
                """
            )
        except Exception:
            # If the column does not exist for some reason, just ignore silently
            pass


# -------------------------------------------------
# Data access helpers used by Streamlit app
# -------------------------------------------------

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
        SELECT C.CONTRIBUTIONDATE,
               C.AMOUNT,
               M.CAMPAIGNNAME
        FROM CONTRIBUTION C
        JOIN CAMPAIGN M ON C.CAMPAIGNID = M.CAMPAIGNID
        WHERE C.ALUMNIID = :aid
        ORDER BY C.CONTRIBUTIONDATE DESC
        """
    )
    return pd.read_sql(sql, engine, params={"aid": alumni_id})


def update_alumni_contact(alumni_id: int, email: str, phone: str, mailing_list: str) -> None:
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
            {"email": email, "phone": phone, "ml": mailing_list, "aid": alumni_id},
        )


def get_campaigns() -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM CAMPAIGN", engine)


def create_contribution(alumni_id: int, campaign_id: int, amount: float, date_str: str) -> None:
    """Insert a new contribution record."""
    with engine.begin() as conn:
        next_id = conn.execute(
            text("SELECT COALESCE(MAX(CONTRIBUTIONID), 9000) + 1 AS nid FROM CONTRIBUTION")
        ).scalar()

        conn.execute(
            text(
                """
                INSERT INTO CONTRIBUTION (CONTRIBUTIONID, ALUMNIID, CAMPAIGNID, CONTRIBUTIONDATE, AMOUNT)
                VALUES (:cid, :aid, :camp, :cdate, :amt)
                """
            ),
            {
                "cid": int(next_id),
                "aid": int(alumni_id),
                "camp": int(campaign_id),
                "cdate": date_str,
                "amt": float(amount),
            },
        )


def get_all_contributions() -> pd.DataFrame:
    sql = """
        SELECT
            C.CONTRIBUTIONDATE,
            A.FIRSTNAME,
            A.LASTNAME,
            M.CAMPAIGNNAME,
            C.AMOUNT
        FROM CONTRIBUTION C
        JOIN ALUMNI  A ON C.ALUMNIID  = A.ALUMNIID
        JOIN CAMPAIGN M ON C.CAMPAIGNID = M.CAMPAIGNID
        ORDER BY C.CONTRIBUTIONDATE DESC
    """
    return pd.read_sql(sql, engine)


def get_employer_summary() -> pd.DataFrame:
    """Return one row per employer with a count of distinct alumni there."""
    sql = """
        SELECT
            EMPLOYERNAME,
            INDUSTRY,
            COUNT(DISTINCT ALUMNIID) AS NUM_ALUMNI
        FROM EMPLOYMENT
        GROUP BY EMPLOYERNAME, INDUSTRY
        ORDER BY NUM_ALUMNI DESC
    """
    return pd.read_sql(sql, engine)


def get_summary_stats() -> dict:
    """Aggregates used by the admin dashboard metrics."""
    # --- totals we can safely get directly with SQL ---
    with engine.begin() as conn:
        total_alumni = conn.execute(
            text("SELECT COUNT(*) FROM ALUMNI")
        ).scalar() or 0

        active_campaigns = conn.execute(
            text("SELECT COUNT(*) FROM CAMPAIGN WHERE STATUS = 'Active'")
        ).scalar() or 0

        total_contributions = conn.execute(
            text("SELECT COALESCE(SUM(AMOUNT), 0) FROM CONTRIBUTION")
        ).scalar() or 0.0

    # --- total employers: use pandas so we don't depend on a specific schema ---
    try:
        emp_df = pd.read_sql("SELECT * FROM EMPLOYMENT", engine)

        if emp_df.empty:
            total_employers = 0
        elif "EMPLOYERNAME" in emp_df.columns:
            total_employers = emp_df["EMPLOYERNAME"].nunique()
        else:
            total_employers = emp_df["ALUMNIID"].nunique()
    except Exception:
        total_employers = 0

    return {
        "total_alumni": int(total_alumni),
        "total_employers": int(total_employers),
        "total_campaigns": int(active_campaigns),
        "total_contributions": float(total_contributions),
    }
