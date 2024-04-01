#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error
from ServiceCheckScripts import Results
from typing import Optional


def update_team_points(team_id: int, points: int, cursor, connection):
    """
    Update the points of a specific team in the `teams` table using a more concise approach.

    Parameters:
    - team_id (int): The ID of the team to update.
    - points_to_add (int): The number of points to add to the team's current points.
    """
    # Define points based on result_code
    print(team_id)
    update_team_points_statement = (
        f"UPDATE teams set points = points + %s WHERE team_id = %s;",
        (points, team_id),
    )

    try:
        cursor.execute(update_team_points_statement)
        # Commit the transaction
        connection.commit()
    except mysql.connector.Error as error:
        print(f"Failed to update points for team: {team_id} \nError: {error}\n")


def update_service_status(
    team_id: int,
    target_id: int,
    service_name: str,
    port_number: Optional[str],
    result_code: Optional[Results.ResultCode],
    participant_feedback: str,
    staff_feedback: str,
    points_obtained: int,
    cursor,
    connection,
):
    """
    Update a port/service row in the database.
    :param service_name: The primary key to identify the port row.
    :param port_number: The port number to be updated (optional).
    :param result_code: The result code to be updated (optional).
    :param participant_feedback: The participant feedback to be updated (optional).
    :param staff_feedback: The staff feedback to be updated (optional).
    :param points_obtained: The points obtained to be updated (optional).
    :param target_id: The target id to be updated (optional).
    """
    update_service_statement = "UPDATE ports SET "
    statement_elements = []
    if port_number is not None:
        statement_elements.append(f"port_number = '{port_number}'")
        if result_code is not None:
            statement_elements.append(f"result_code = '{result_code}'")
        if participant_feedback is not None:
            statement_elements.append(
                f"participant_feedback = '{participant_feedback}'"
            )
        if staff_feedback is not None:
            statement_elements.append(f"staff_feedback = '{staff_feedback}'")
        if points_obtained is not None:
            statement_elements.append(f"points_obtained = {points_obtained}")
    update_service_statement += ", ".join(statement_elements)
    update_service_statement += f" WHERE service_name = {service_name} AND target_id = {target_id} AND team_id = {team_id}"

    try:
        cursor.execute(update_service_statement)
        # Commit the transaction
        connection.commit()
    except mysql.connector.Error as error:
        print(
            f"Failed to update service: {service_name}\nFor team: {team_id} \nError: {error}\n"
        )


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
                "SELECT * FROM teams WHERE team_id = %s", (health_check.team_id)
            )

            team = cursor.fetchone()
            if team:
                print("Team exists, scoring team: %s", team)
                # Update a team's points
                update_team_points(
                    int(health_check.team_id), health_check.points, cursor, connection
                )

                # Update a single service status
                update_service_status(
                    int(health_check.team_id),
                    int(health_check.target_host),
                    health_check.service_name,
                    health_check.target_port,
                    health_check.result.result,
                    health_check.result.feedback,
                    health_check.result.staff_feedback,
                    health_check.points,
                    cursor,
                    connection,
                )

            else:
                raise ValueError("That Team Does Not Exist in DB.")

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
