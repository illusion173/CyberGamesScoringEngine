import mysql.connector
from mysql.connector import Error
from Results import ServiceHealthCheck


def update_team_points(team_id: int, result_code: str, cursor):
    """Update team points based on result code."""
    # Define points based on result_code
    points_awarded = {"success": 10}  # Add other result codes if needed
    points_to_add = points_awarded.get(result_code, 0)

    if points_to_add > 0:
        update_query = "UPDATE teams SET points = points + %s WHERE id = %s"
        cursor.execute(update_query, (points_to_add, team_id))
        print(f"Added {points_to_add} points to team ID {team_id}")


def insert_service_health_check(health_check: ServiceHealthCheck, team_name: str):
    try:
        connection = mysql.connector.connect(
            host="your_database_host",
            database="health_checks",
            user="your_database_user",
            password="your_database_password",
        )

        if connection.is_connected():
            cursor = connection.cursor()
            # Ensure the team exists or create it
            cursor.execute("SELECT id FROM teams WHERE name = %s", (team_name))
            team = cursor.fetchone()
            if team:
                team_id = team[0]
            else:
                cursor.execute("INSERT INTO teams (name) VALUES (%s)", (team_name,))
                team_id = cursor.lastrowid

            # Insert into service_checks table
            insert_query = """
                INSERT INTO service_checks (team_id, target_host, result_code, participant_feedback, staff_feedback)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(
                insert_query,
                (
                    team_id,
                    health_check.target_host,
                    health_check.result.result.value,
                    health_check.result.feedback,
                    health_check.result.staff_feedback,
                ),
            )
            service_check_id = cursor.lastrowid

            # Update team points based on result code
            update_team_points(team_id, health_check.result.result.value, cursor)

            # Insert participant and staff details as before...
            # (Omitted for brevity; see previous example)

            # Insert participant details
            for detail in health_check.result._participant_result.details:
                cursor.execute(
                    "INSERT INTO check_details (service_check_id, detail_type, detail) VALUES (%s, 'participant', %s)",
                    (service_check_id, detail),
                )

            # Insert staff details
            for detail in health_check.result._staff_result.details:
                cursor.execute(
                    "INSERT INTO check_details (service_check_id, detail_type, detail) VALUES (%s, 'staff', %s)",
                    (service_check_id, detail),
                )

            connection.commit()
            print(
                f"Service health check inserted successfully with id {service_check_id}"
            )

            connection.commit()
            print(
                f"Service health check inserted successfully with id {service_check_id}"
            )

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


# Example usage
# Assuming you have a health_check object and a team name
# insert_service_health_check(health_check, "Team Name")
