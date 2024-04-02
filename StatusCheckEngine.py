#!/usr/bin/env python3
import asyncio
from ServiceCheckScripts import PrepareServiceChecks
from ServiceCheckScripts import ExecuteServiceCheck
from ServiceCheckScripts import ImportEnvVars
from ServiceCheckScripts import Scoring
from DBScripts import DBConnector


async def main():
    try:
        # Targets must be able to be loaded to start program
        loaded_vars = ImportEnvVars.load_env_vars()
        while True:
            prepare_service_checks = PrepareServiceChecks.prepare_service_check(
                loaded_vars
            )
            # Create a list of coroutine objects for each service check
            tasks = [
                ExecuteServiceCheck.arrange_service_check(service_check)
                for service_check in prepare_service_checks
            ]

            # Use asyncio.as_completed to process results as they become available
            for coro in asyncio.as_completed(tasks):

                result = await coro  # Wait for the next task to complete

                # Score all the service checks here
                scored_service_check = Scoring.score_health_check(result)
                print(scored_service_check.service_name)
                print(scored_service_check.result.result)
                # RESULT HANDLING HERE
                # UNCOMMENT to enable scoring
                # DBConnector.insert_service_health_check(scored_service_check)

            # Wait 5 seconds, reattempt targets.
            await asyncio.sleep(20)
    except KeyboardInterrupt:
        print("\nCtrl+C Detected, Quitting Status Check Engine.")


if __name__ == "__main__":
    asyncio.run(main())
