from ServiceCheckScripts import Results


def prepare_service_check(loaded_env_dict: dict) -> list:
    prepared_service_checks = []

    for team in loaded_env_dict["TEAMS"]:
        # Grab target list
        target_list = team["TARGETS"]
        for target in target_list:
            # We need to create a new Service Check
            new_service_health_check = Results.ServiceHealthCheck(
                target_host=str(target["IP"]),
                target_port=str(target["PORT"]),
                team_id=str(team["TEAM_ID"]),
                team_name=str(team["TEAM_NAME"]),
            )
            prepared_service_checks.append(new_service_health_check)

    return prepared_service_checks
