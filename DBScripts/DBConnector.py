#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error
from ServiceCheckScripts import Results


def update_team_points(team_id: int, result_code: str, cursor):
    """Update team points based on result code."""
    # Define points based on result_code
    points_awarded = {"success": 10}  # Add other result codes if needed
    points_to_add = points_awarded.get(result_code, 0)

    if points_to_add > 0:
        update_query = "UPDATE teams SET points = points + %s WHERE id = %s"
        cursor.execute(update_query, (points_to_add, team_id))
        print(f"Added {points_to_add} points to team ID {team_id}")


def insert_service_health_check(health_check: Results.ServiceHealthCheck):
    try:
        connection = mysql.connector.connect(
            host="your_database_host",
            database="health_checks",
            user="your_database_user",
            password="your_database_password",
        )

        if connection.is_connected():
            cursor = connection.cursor()
            # Ensure the team exists
            cursor.execute(
                "SELECT id FROM teams WHERE name = %s", (health_check.team_name)
            )
            team = cursor.fetchone()
            if team:
                print("SUBMITTING!")
            else:
                raise ValueError("That Team Does Not Exist in DB.")

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
