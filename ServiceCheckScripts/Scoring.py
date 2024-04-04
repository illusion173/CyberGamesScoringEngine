from .Results import ServiceHealthCheck, ResultCode
import sys


def score_generic(
    given_service_health_check: ServiceHealthCheck, pass_score: int, warn_score: int = 0
) -> int:
    match given_service_health_check.result.result:
        case ResultCode.PASS:
            return pass_score
        case ResultCode.WARN:
            return warn_score
        case _:
            return 0


def score_icmp(given_service_health_check: ServiceHealthCheck) -> int:
    return score_generic(given_service_health_check, pass_score=5)


def score_ssh(given_service_health_check: ServiceHealthCheck) -> int:
    return score_generic(given_service_health_check, pass_score=25, warn_score=10)


# TO DO
def score_ftp(given_service_health_check: ServiceHealthCheck) -> int:
    return score_generic(given_service_health_check, pass_score=40, warn_score=10)


def score_http(given_service_health_check: ServiceHealthCheck) -> int:
    return score_generic(given_service_health_check, pass_score=25, warn_score=10)


def score_health_check(
    given_service_health_check: ServiceHealthCheck,
) -> ServiceHealthCheck:
    scoring_functions = {
        "ICMP": score_icmp,
        "FTP": score_ftp,
        "SSH": score_ssh,
        "HTTP": score_http,
    }

    scoring_function = scoring_functions.get(given_service_health_check.service_name)
    if scoring_function:
        given_service_health_check.points = scoring_function(given_service_health_check)
    else:
        print("ERROR, while scoring...")
        sys.exit(0)

    return given_service_health_check
