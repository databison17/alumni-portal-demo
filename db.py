from sqlalchemy import create_engine, text
import pandas as pd
import os

# SQLite file in the same folder as the app
DB_URL = "sqlite:///alumni.db"
engine = create_engine(DB_URL, echo=False)

def init_db():
    """Create tables if they don't exist and seed with sample data."""
    with engine.begin() as conn:
        # Create tables (compatible with SQLite)
        conn.exec_driver_sql("""
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
        """)

        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS DEGREE (
            DEGREEID  INTEGER PRIMARY KEY,
            ALUMNIID  INTEGER NOT NULL,
            MAJOR     TEXT NOT NULL,
            MINOR     TEXT NOT NULL,
            SCHOOL    TEXT NOT NULL,
            HONORS    TEXT NOT NULL,
            GRADMONTH TEXT NOT NULL,
            GRADYEAR  INTEGER NOT NULL,
            FOREIGN KEY (ALUMNIID) REFERENCES ALUMNI(ALUMNIID)
        );
        """)

        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS EMPLOYER (
            EMPLOYERID   INTEGER PRIMARY KEY,
            EMPLOYERNAME TEXT NOT NULL,
            INDUSTRY     TEXT NOT NULL,
            WEBSITE      TEXT NOT NULL,
            HQ_CITY      TEXT NOT NULL,
            HQ_STATE     TEXT NOT NULL,
            HQ_COUNTRY   TEXT NOT NULL
        );
        """)

        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS EMPLOYMENT (
            EMPLOYMENTID INTEGER PRIMARY KEY,
            ALUMNIID     INTEGER NOT NULL,
            EMPLOYERID   INTEGER NOT NULL,
            JOBTITLE     TEXT NOT NULL,
            DEPARTMENT   TEXT NOT NULL,
            EMP_STARTDATE TEXT NOT NULL,
            FOREIGN KEY (ALUMNIID) REFERENCES ALUMNI(ALUMNIID),
            FOREIGN KEY (EMPLOYERID) REFERENCES EMPLOYER(EMPLOYERID)
        );
        """)

        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS ALUMNIASSOCIATION (
            ASSOCIATIONID   INTEGER PRIMARY KEY,
            ASSOCIATIONNAME TEXT NOT NULL,
            CHAPTERREGION   TEXT NOT NULL,
            ASS_ACTIVE      TEXT NOT NULL
        );
        """)

        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS ALUMNIMEMBERSHIP (
            MEMBERSHIPID  INTEGER PRIMARY KEY,
            ALUMNIID      INTEGER NOT NULL,
            ASSOCIATIONID INTEGER NOT NULL,
            MEM_STARTDATE TEXT NOT NULL,
            MEM_ENDDATE   TEXT NOT NULL,
            MEM_STATUS    TEXT NOT NULL,
            MEM_ROLE      TEXT NOT NULL,
            FOREIGN KEY (ALUMNIID) REFERENCES ALUMNI(ALUMNIID),
            FOREIGN KEY (ASSOCIATIONID) REFERENCES ALUMNIASSOCIATION(ASSOCIATIONID)
        );
        """)

        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS CAMPAIGN (
            CAMPAIGNID     INTEGER PRIMARY KEY,
            CAMPAIGNNAME   TEXT NOT NULL,
            FUNCODE        INTEGER NOT NULL,
            CAMP_STARTDATE TEXT NOT NULL,
            CAMP_ENDDATE   TEXT NOT NULL,
            GOALAMOUNT     REAL NOT NULL
        );
        """)

        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS CONTRIBUTION (
            CONTRIBUTIONID  INTEGER PRIMARY KEY,
            ALUMNIID        INTEGER NOT NULL,
            CAMPAIGNID      INTEGER NOT NULL,
            CONTRIBUTIONDATE TEXT NOT NULL,
            AMOUNT          REAL NOT NULL,
            FOREIGN KEY (ALUMNIID)   REFERENCES ALUMNI(ALUMNIID),
            FOREIGN KEY (CAMPAIGNID) REFERENCES CAMPAIGN(CAMPAIGNID)
        );
        """)

        # Seed only if ALUMNI table is empty
        count = conn.execute(text("SELECT COUNT(*) FROM ALUMNI")).scalar()
        if count == 0:
            conn.exec_driver_sql("""
            INSERT INTO ALUMNI VALUES
            (1001, 'Maya', 'Johnson', 'maya.johnson@email.com', '202-555-7821', 2018, 'Finance','Yes'),
            (1002, 'Jordan', 'Smith', 'jordan.smith@email.com', '404-555-6719', 2019, 'Marketing','No'),
            (1003, 'Amira', 'Patel', 'amira.patel@email.com', '312-555-2190', 2020, 'Computer Information Systems','Yes'),
            (1004, 'Isaiah', 'Thompson','isaiah.thompson@email.com', '443-555-9898', 2017, 'Finance','Yes'),
            (1005, 'Nia', 'Brown', 'nia.brown@email.com', '703-555-3104', 2021, 'Supply Chain','Yes');
            """)

            conn.exec_driver_sql("""
            INSERT INTO DEGREE VALUES
            (3001,1001,'Finance','None','Howard University School of Business','Cum Laude','May',2018),
            (3002,1002,'Marketing','None','Howard University School of Business','Magna Cum Laude','May',2019),
            (3003,1003,'Computer Information Systems','Business Analytics','Howard University School of Business','Summa Cum Laude','May',2020);
            """)

            conn.exec_driver_sql("""
            INSERT INTO EMPLOYER VALUES
            (4001,'Goldman Sachs','Finance','https://www.goldmansachs.com','New York','NY','USA'),
            (4002,'Google','Technology','https://www.google.com','Mountain View','CA','USA'),
            (4003,'Amazon','E-commerce','https://www.amazon.com','Seattle','WA','USA');
            """)

            conn.exec_driver_sql("""
            INSERT INTO EMPLOYMENT VALUES
            (5001,1001,4001,'Investment Banking Analyst','Global Markets','2019-07-01'),
            (5002,1002,4003,'Marketing Specialist','Brand Marketing','2020-09-15'),
            (5003,1003,4002,'Associate Product Manager','Cloud Services','2021-08-01');
            """)

            conn.exec_driver_sql("""
            INSERT INTO ALUMNIASSOCIATION VALUES
            (6001,'Howard Business Alumni Association - Northeast','Northeast Region','Active'),
            (6002,'Howard Business Alumni Association - West Coast','West Coast Region','Active');
            """)

            conn.exec_driver_sql("""
            INSERT INTO ALUMNIMEMBERSHIP VALUES
            (7001,1001,6001,'2019-09-01','9999-12-31','Active','Member'),
            (7002,1002,6002,'2020-10-01','9999-12-31','Active','Officer');
            """)

            conn.exec_driver_sql("""
            INSERT INTO CAMPAIGN VALUES
            (8001,'Business School Scholarship Fund',101,'2022-01-01','2022-12-31',100000.00),
            (8002,'Technology Innovation Lab',102,'2023-01-01','2023-12-31',150000.00);
            """)

            conn.exec_driver_sql("""
            INSERT INTO CONTRIBUTION VALUES
            (9001,1001,8001,'2022-03-15',5000.00),
            (9002,1003,8002,'2023-06-20',2500.00);
            """)

def get_alumni():
    return pd.read_sql("SELECT * FROM ALUMNI", engine)

def get_alumni_by_id(alumni_id: int):
    sql = text("SELECT * FROM ALUMNI WHERE ALUMNIID = :aid")
    return pd.read_sql(sql, engine, params={"aid": int(alumni_id)})

def get_degrees_for_alumni(alumni_id: int):
    sql = text("SELECT * FROM DEGREE WHERE ALUMNIID = :aid")
    return pd.read_sql(sql, engine, params={"aid": int(alumni_id)})

def get_employment_for_alumni(alumni_id: int):
    sql = text("""
        SELECT e.JOBTITLE, e.DEPARTMENT, e.EMP_STARTDATE,
               emp.EMPLOYERNAME, emp.INDUSTRY,
               emp.HQ_CITY, emp.HQ_STATE, emp.HQ_COUNTRY
        FROM EMPLOYMENT e
        JOIN EMPLOYER emp ON e.EMPLOYERID = emp.EMPLOYERID
        WHERE e.ALUMNIID = :aid
    """)
    return pd.read_sql(sql, engine, params={"aid": int(alumni_id)})

def get_memberships_for_alumni(alumni_id: int):
    sql = text("""
        SELECT aa.ASSOCIATIONNAME, aa.CHAPTERREGION,
               am.MEM_STARTDATE, am.MEM_ENDDATE,
               am.MEM_STATUS, am.MEM_ROLE
        FROM ALUMNIMEMBERSHIP am
        JOIN ALUMNIASSOCIATION aa
          ON am.ASSOCIATIONID = aa.ASSOCIATIONID
        WHERE am.ALUMNIID = :aid
    """)
    return pd.read_sql(sql, engine, params={"aid": int(alumni_id)})

def get_contributions_for_alumni(alumni_id: int):
    sql = text("""
        SELECT c.CONTRIBUTIONDATE, c.AMOUNT,
               camp.CAMPAIGNNAME
        FROM CONTRIBUTION c
        JOIN CAMPAIGN camp ON c.CAMPAIGNID = camp.CAMPAIGNID
        WHERE c.ALUMNIID = :aid
    """)
    return pd.read_sql(sql, engine, params={"aid": int(alumni_id)})

def get_summary_stats():
    stats = {}
    stats["total_alumni"] = pd.read_sql(
        "SELECT COUNT(*) AS cnt FROM ALUMNI", engine)["cnt"][0]
    stats["total_employers"] = pd.read_sql(
        "SELECT COUNT(*) AS cnt FROM EMPLOYER", engine)["cnt"][0]
    stats["total_campaigns"] = pd.read_sql(
        "SELECT COUNT(*) AS cnt FROM CAMPAIGN", engine)["cnt"][0]
    stats["total_contributions"] = float(pd.read_sql(
        "SELECT COALESCE(SUM(AMOUNT),0) AS total FROM CONTRIBUTION", engine)["total"][0])
    return stats


def update_alumni_contact(alumni_id: int, email: str, phone: str, mailing_list: str):
    with engine.begin() as conn:
        sql = text("""
            UPDATE ALUMNI
            SET PRIMARYEMAIL = :email,
                PHONE = :phone,
                MAILING_LIST = :ml
            WHERE ALUMNIID = :aid
        """)
        conn.execute(sql, {"email": email, "phone": phone, "ml": mailing_list, "aid": alumni_id})

def get_campaigns():
    return pd.read_sql("SELECT * FROM CAMPAIGN", engine)

def create_contribution(alumni_id: int, campaign_id: int, amount: float, date_str: str):
    with engine.begin() as conn:
        next_id = conn.execute(
            text("SELECT COALESCE(MAX(CONTRIBUTIONID), 9000) + 1 AS nid FROM CONTRIBUTION")
        ).scalar()
        sql = text("""
            INSERT INTO CONTRIBUTION (CONTRIBUTIONID, ALUMNIID, CAMPAIGNID, CONTRIBUTIONDATE, AMOUNT)
            VALUES (:cid, :aid, :camp, :cdate, :amt)
        """)
        conn.execute(sql, {
            "cid": int(next_id),
            "aid": int(alumni_id),
            "camp": int(campaign_id),
            "cdate": date_str,
            "amt": float(amount)
        })
