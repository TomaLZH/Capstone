import os
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, LargeBinary

# Set Google Cloud credentials for authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ardent-kite-449907-q5-3b3009718cce.json"


def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of PostgreSQL.
    Uses the Cloud SQL Python Connector.
    """
    # Define Cloud SQL instance details
    instance_connection_name = "ardent-kite-449907-q5:us-central1:capstone"
    db_user = "ZH"
    db_pass = "password"  # Ensure this is stored securely (e.g., Secret Manager)
    db_name = "postgres"

    # Determine IP type (Public or Private)
    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    # Initialize Cloud SQL Python Connector
    connector = Connector()

    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )
        return conn

    # Create the SQLAlchemy engine
    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )

    return engine


# Test the connection
engine = connect_with_connector()
try:
    with engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("SELECT version();"))
        print("✅ Connected to PostgreSQL! Version:", result.scalar())
except Exception as e:
    print("❌ Connection failed:", e)


# Define table metadata
metadata = MetaData()

# Define the table structure
my_table = Table(
    'my_table', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(50)),
    Column('password', String(50)),
    Column('data', LargeBinary)
)

metadata.create_all(engine)
