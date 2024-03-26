import yaml
import json

YAMLFILENAME = "EnvVars.yaml"


def load_yaml(filename):
    with open(filename, "r") as file:
        yaml_data = yaml.safe_load(file)
    return yaml_data


def yaml_to_json(yaml_data):
    json_data = json.loads(json.dumps(yaml_data))
    return json_data


def load_env_vars():
    yaml_data = load_yaml(YAMLFILENAME)
    env_vars = yaml_to_json(yaml_data)

    for team in env_vars["TEAMS"]:
        print(team["TEAM_NAME"])
        print(team["TEAM_ID"])

    return env_vars


load_env_vars()
