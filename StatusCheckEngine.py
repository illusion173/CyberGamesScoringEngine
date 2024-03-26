#!/usr/bin/env python3
import asyncio
import sys
from Results import ServiceHealthCheck
from ImportEnvVars import load_env_vars
from ServiceCheckScripts import CheckIcmp, CheckFTP, CheckSSH
from DBScripts import DBConnector


def prepare_service_check(Loaded_Vars: dict) -> list:
    prepared_service_checks = []

    for team in Loaded_Vars["TEAMS"].values():
        # We need to create a new Service Check
        newServicHealthCheck = ServiceHealthCheck(
            target_host=str(0),
            target_port=str(0),
            team_id=str(team["TEAM_ID"]),
            team_name=str(team["TEAM_NAME"]),
        )

        for targets in team:



        prepared_service_checks.append(
            ServiceHealthCheck(
                target_host=target["IP"],
                target_port=str(target["PORT"]),
                team_id=str(target["TEAM_ID"]),
                team_name=str(team["TEAM_NAME"]),
            )
        )

    return prepared_service_checks


async def arrange_service_check(service_check):
    port = service_check.target_port

    match port:
        case "ICMP":
            print("ICMP CHECK")
            result = await CheckIcmp.ICMPCheck(service_check).execute()
        case "21":
            result = ""
            print("FTP CHECK")
            # Handle other cases similarly
            result = await CheckFTP.FTPCheck(service_check).execute()
        case "22":
            result = ""
            print("SSH CHECK")
            result = await CheckSSH.SSHCheck(service_check).execute()
        case _:
            print("ERROR, No service or Port Inputted?")
            sys.exit(0)

    return result


async def main():
    try:
        # Targets must be able to be loaded to start program
        loaded_vars = load_env_vars()
        while True:
            prepare_service_checks = prepare_service_check(loaded_vars)
            # Create a list of coroutine objects for each service check
            tasks = [
                arrange_service_check(service_check)
                for service_check in prepare_service_checks
            ]

            # Use asyncio.as_completed to process results as they become available
            for coro in asyncio.as_completed(tasks):
                result = await coro  # Wait for the next task to complete
                print(result.result.result)
                # RESULT HANDLING HERE
                # insert_service_health_check(result, "TEST")

            # Wait 5 seconds, reattempt targets.
            await asyncio.sleep(20)
    except KeyboardInterrupt:
        print("\nCtrl+C Detected, Quitting Status Check Engine.")


if __name__ == "__main__":
    asyncio.run(main())
