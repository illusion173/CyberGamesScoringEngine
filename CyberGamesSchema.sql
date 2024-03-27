CREATE DATABASE IF NOT EXISTS health_checks;
USE health_checks;

CREATE TABLE IF NOT EXISTS teams (
  team_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  points INT DEFAULT 0
)

CREATE TABLE IF NOT EXISTS targets (
  target_id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT,
  target_host VARCHAR(255) NOT NULL,
  FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL
)

CREATE TABLE IF NOT EXISTS ports (
  port_id INT AUTO_INCREMENT PRIMARY KEY,
  target_id VARCHAR(255) NOT NULL
  port_number VARCHAR(255) NOT NULL
  service_name VARCHAR(255) NOT NULL
  result_code ENUM('success', 'failure', 'partial', 'timeout', 'unknown', 'error') NOT NULL,
  participant_feedback TEXT,
  staff_feedback TEXT,
  points_obtained, INT
  FOREIGN KEY (target_id) REFERENCES targets(target_id) ON DELETE SET NULL
)
