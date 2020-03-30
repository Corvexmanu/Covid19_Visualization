from PAMSArchive_connection import get_PAMSArchive_conn
import pandas as pd

conn = get_PAMSArchive_conn()

strQuery = """SELECT TOP 100 * FROM [pams].[tPositions]"""

dftPositions = pd.read_sql(strQuery, conn)

dftPositions.head()

conn.close()