import os
import sys

import MySQLdb
from werkzeug.security import generate_password_hash


def main() -> int:
    mysql_host = os.environ.get("MYSQL_HOST") or os.environ.get("MYSQLHOST")
    mysql_port = int(os.environ.get("MYSQL_PORT") or os.environ.get("MYSQLPORT") or "3306")
    mysql_user = os.environ.get("MYSQL_USER") or os.environ.get("MYSQLUSER")
    mysql_password = os.environ.get("MYSQL_PASSWORD")
    if mysql_password is None:
        mysql_password = os.environ.get("MYSQLPASSWORD")
    mysql_database = os.environ.get("MYSQL_DB") or os.environ.get("MYSQLDATABASE")

    seed_user_email = os.environ.get("SEED_USER_EMAIL", "seed-user@example.invalid")
    seed_authority_email = os.environ.get("SEED_AUTHORITY_EMAIL", "seed-authority@example.invalid")
    seed_admin_email = os.environ.get("SEED_ADMIN_EMAIL", "seed-admin@example.invalid")

    missing_values = [
        name
        for name, value in (
            ("MYSQL_HOST/MYSQLHOST", mysql_host),
            ("MYSQL_USER/MYSQLUSER", mysql_user),
            ("MYSQL_PASSWORD/MYSQLPASSWORD", mysql_password),
            ("MYSQL_DB/MYSQLDATABASE", mysql_database),
            ("SEED_USER_PASSWORD", os.environ.get("SEED_USER_PASSWORD")),
            ("SEED_AUTHORITY_PASSWORD", os.environ.get("SEED_AUTHORITY_PASSWORD")),
            ("SEED_ADMIN_PASSWORD", os.environ.get("SEED_ADMIN_PASSWORD")),
        )
        if value is None or value == ""
    ]

    if missing_values:
        raise RuntimeError(
            "Missing seed environment variables: " + ", ".join(missing_values)
        )

    connection = MySQLdb.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        passwd=mysql_password,
        db=mysql_database,
        charset="utf8mb4",
    )

    cursor = None
    try:
        cursor = connection.cursor()

        seed_accounts = (
            (
                "user",
                seed_user_email,
                os.environ["SEED_USER_PASSWORD"],
                "INSERT INTO users "
                "(first_name, last_name, email_or_phone, password, role) "
                "VALUES (%s, %s, %s, %s, %s)",
                ("Seed", "User", seed_user_email,
                 generate_password_hash(os.environ["SEED_USER_PASSWORD"]), "user"),
                "SELECT user_id FROM users WHERE email_or_phone = %s",
            ),
            (
                "admin",
                seed_admin_email,
                os.environ["SEED_ADMIN_PASSWORD"],
                "INSERT INTO users "
                "(first_name, last_name, email_or_phone, password, role) "
                "VALUES (%s, %s, %s, %s, %s)",
                ("Seed", "Admin", seed_admin_email,
                 generate_password_hash(os.environ["SEED_ADMIN_PASSWORD"]), "admin"),
                "SELECT user_id FROM users WHERE email_or_phone = %s",
            ),
        )

        for role, email, _password, insert_sql, insert_values, lookup_sql in seed_accounts:
            cursor.execute(lookup_sql, (email,))
            if cursor.fetchone():
                print(f"Skipped existing {role} account: {email}")
            else:
                cursor.execute(insert_sql, insert_values)
                print(f"Created {role} account: {email}")

        cursor.execute(
            "SELECT authority_id FROM authority WHERE email = %s",
            (seed_authority_email,),
        )
        if cursor.fetchone():
            print(f"Skipped existing authority account: {seed_authority_email}")
        else:
            cursor.execute(
                """
                INSERT INTO authority
                    (authority_type, authority_name, email, password,
                     location, license_number, status, document)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    "organization",
                    "Seed Authority",
                    seed_authority_email,
                    generate_password_hash(os.environ["SEED_AUTHORITY_PASSWORD"]),
                    "Placeholder location",
                    None,
                    "approved",
                    None,
                ),
            )
            print(f"Created authority account: {seed_authority_email}")

        connection.commit()
        return 0
    except Exception:
        connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (MySQLdb.Error, RuntimeError) as error:
        print(f"Seed failed: {error}", file=sys.stderr)
        sys.exit(1)
