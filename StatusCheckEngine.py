import json
from Results import ServiceHealthCheck
from ImportEnvVars import load_env_vars
from CheckIcmp import ICMPCheck
import json


def prepare_service_check(Loaded_Vars: dict) -> list:
    prepared_service_checks = []

    for target in Loaded_Vars["TARGETS"].values():
        prepared_service_checks.append(ServiceHealthCheck(ip_host=target["IP"]))

    return prepared_service_checks


# This is where the overall engine will check each service, and write it to a database, for rn just json
def main():
    Loaded_Vars = load_env_vars()
    prepare_service_checks = prepare_service_check(Loaded_Vars)
    try:
        while True:
            for service_check in prepare_service_checks:
                icmp_check = ICMPCheck(service_check)
                result = icmp_check.execute()
                print(result.result.result)
                print(result.result.feedback)
    except KeyboardInterrupt:
        print("\nCtrl+C Detected, Quitting Status Check Engine.")


if __name__ == "__main__":
    main()
