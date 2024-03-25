import yaml
import json

yaml_filename = "env_vars.yaml"


def load_yaml(filename):
    with open(filename, "r") as file:
        yaml_data = yaml.safe_load(file)
    return yaml_data


def yaml_to_json(yaml_data):
    json_data = json.loads(json.dumps(yaml_data))
    return json_data


# Load YAML data
yaml_data = load_yaml(yaml_filename)

# Convert YAML to JSON
json_data = yaml_to_json(yaml_data)


def load_env_vars():
    yaml_data = load_yaml(yaml_filename)
    env_vars = yaml_to_json(yaml_data)

    return env_vars
