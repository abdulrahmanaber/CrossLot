
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


def get_sql_server_engine():

    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=BODY;"
        "DATABASE=CrossLotDW;"
        "Trusted_Connection=yes;"
    )

    connection_url = (
        "mssql+pyodbc:///?odbc_connect="
        + quote_plus(connection_string)
    )

    engine = create_engine(connection_url)

    return engine


if __name__ == "__main__":

    engine = get_sql_server_engine()

    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT DB_NAME()")
        )

        print("Connected successfully!")
        print("Database:", result.scalar())

    engine.dispose()
