import sys
from ServiceCheckScripts import CheckIcmp, CheckFTP, CheckSSH
from Scoring import ScoreService


async def arrange_service_check(service_check):
    port = service_check.target_port
    scoring_service = ScoreService()

    match port:
        case "ICMP":
            print("ICMP CHECK")
            result = await CheckIcmp.ICMPCheck(service_check).execute()
            result.points = scoring_service.score_icmp(
                given_service_health_check=result
            )

        case "21":
            result = ""
            print("FTP CHECK")
            result = await CheckFTP.FTPCheck(service_check).execute()
            result.points = scoring_service.score_ftp(result)
        case "22":
            result = ""
            print("SSH CHECK")
            result = await CheckSSH.SSHCheck(service_check).execute()
            result.points = scoring_service.score_ssh(result)
        case _:
            print("ERROR, No service or Port Inputted? Call Staff.")
            sys.exit(0)

    return result
