#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error


def insert_team(entered_team_name: str):
    try:
        connection = mysql.connector.connect(
            host="your_database_host",
            database="health_checks",
            user="your_database_user",
            password="your_database_password",
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM teams WHERE name = %s", (entered_team_name))
            team = cursor.fetchone()
            # If the team exists
            if team:
                print("Team {} already exists, exiting program!", team)
            # if team does not exist
            else:
                cursor.execute(
                    "INSERT INTO teams (name) VALUES (%s)", (entered_team_name,)
                )
                cursor.execute(
                    "SELECT id FROM teams WHERE name = %s", (entered_team_name)
                )
                team_id = cursor.fetchone()
                print("-------------------------------------")
                print("SUCCESSFUL CREATION OF TEAM %s", entered_team_name)
                print("NEEDED INFO FOR YAML FILE")
                print("TEAM_NAME: %s", entered_team_name)
                print("TEAM_ID: %s", team_id)

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
        print("Exiting....")


def get_string_input(prompt):
    while True:
        user_input = input(prompt)
        # Check if the input contains only letters
        if user_input.isalpha():
            return user_input
        print("Invalid input. Please enter a string without any numbers.")


def main():
    print("Team Generation Program\n")
    try:

        while True:
            print("--------------------------")
            user_team_name = get_string_input(
                "Enter a Team Name (string without any numbers): "
            )
            if user_team_name:
                insert_team(user_team_name)
    except KeyboardInterrupt:
        print("\nCtrl+C Detected, Quitting Team Generation Program.")


if __name__ == "__main__":
    main()
