import time
from Results import ServiceHealthCheck
from ImportEnvVars import load_env_vars
from CheckIcmp import ICMPCheck
from DBConnector import insert_service_health_check
import asyncio


def prepare_service_check(Loaded_Vars: dict) -> list:
    prepared_service_checks = []

    for target in Loaded_Vars["TARGETS"].values():
        prepared_service_checks.append(
            ServiceHealthCheck(
                target_host=target["IP"], target_port=str(target["PORT"])
            )
        )

    return prepared_service_checks


async def arrange_service_check(service_check):
    port = service_check.target_port

    match port:
        case "ICMP":
            print("ICMP")
            result = await ICMPCheck(service_check).execute()
            print(result.result.result)
        case "21":
            print("FTP")
            # Handle other cases similarly
        case "22":
            print("SSH")


async def main():
    try:
        # Targets must be able to be loaded to start program
        loaded_vars = load_env_vars()
        while True:
            # Every 5 seconds, reattempt targets.
            prepare_service_checks = prepare_service_check(loaded_vars)
            for service_check in prepare_service_checks:
                result = await arrange_service_check(service_check)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nCtrl+C Detected, Quitting Status Check Engine.")


if __name__ == "__main__":
    # main()
    asyncio.run(main())
