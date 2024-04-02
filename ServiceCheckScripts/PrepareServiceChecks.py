from ServiceCheckScripts import Results


def prepare_service_check(loaded_env_dict: dict) -> list:
    prepared_service_checks = []

    for team in loaded_env_dict["TEAMS"]:
        # Grab target list
        target_list = team["TARGETS"]
        for target in target_list:
            # We need to grab the actions list
            actions_list = target["ACTIONS"]
            for action in actions_list:
                new_ssh_info = None
                new_http_info = None
                new_ftp_info = None
                service_name = action["SERVICE_NAME"]

                match service_name:
                    case "SSH":
                        new_ssh_info = Results.SSHInfo()
                        new_ssh_info.ssh_username = action["SSH_USERNAME"]
                        new_ssh_info.ssh_priv_key = action["SSH_PRIV_KEY"]
                        new_ssh_info.md5sum = action["MD5_SUM"]
                        new_ssh_info.ssh_script = action["SSH_SCRIPT"]
                    case "HTTP":
                        new_http_info = Results.HTTPInfo()
                        new_http_info.url = action["URL"]
                        new_http_info.path = action["PATH"]
                    case "FTP":
                        new_ftp_info = Results.FTPInfo()
                        new_ftp_info.ftp_username = action["FTP_USERNAME"]
                        new_ftp_info.ftp_password = action["FTP_PASSWORD"]
                        new_ftp_info.files = action["FILES"]
                    case _:
                        None

                new_service_health_check = Results.ServiceHealthCheck(
                    target_host=str(target["IP"]),
                    target_port=str(action.get("PORT", None)),
                    team_id=str(team["TEAM_ID"]),
                    team_name=str(team["TEAM_NAME"]),
                    ssh_info=new_ssh_info,
                    service_name=action["SERVICE_NAME"],
                    http_info=new_http_info,
                )
                prepared_service_checks.append(new_service_health_check)

    return prepared_service_checks
