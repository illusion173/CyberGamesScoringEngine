from ServiceCheckScripts import Results


def prepare_service_check(loaded_env_dict: dict) -> list:
    prepared_service_checks = []

    for team in loaded_env_dict["TEAMS"]:
        # Grab target list
        target_list = team["TARGETS"]
        for target in target_list:
            # We need to grab the actions list
            actions_list = target_list["ACTIONS"]
            for action in actions_list:
                new_ssh_info = None

                if action["SERVICE_NAME"] == "SSH":
                    new_ssh_info = Results.SSHInfo()
                    new_ssh_info.ssh_username = action["SSH_USERNAME"]
                    new_ssh_info.ssh_priv_key = action["SSH_PRIV_KEY"]
                    new_ssh_info.md5sum = action["MD5_SUM"]
                    new_ssh_info.ssh_script = action["SSH_SCRIPT"]

                new_service_health_check = Results.ServiceHealthCheck(
                    target_host=str(target["IP"]),
                    target_port=str(action.get("PORT", None)),
                    team_id=str(team["TEAM_ID"]),
                    team_name=str(team["TEAM_NAME"]),
                    ssh_info=new_ssh_info,
                    service_name=action["SERVICE_NAME"],
                )
                prepared_service_checks.append(new_service_health_check)

    return prepared_service_checks
