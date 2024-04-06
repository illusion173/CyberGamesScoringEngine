--
--
CREATE TABLE `targets` (
  `target_id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, 
  `target_host` varchar(255) NOT NULL);
--
-- Create model teams
--
CREATE TABLE `teams` (
  `team_id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, 
  `name` varchar(255) NOT NULL, 
  `points` integer NOT NULL DEFAULT 0);
--
-- Create model ports
--
CREATE TABLE `ports` (
  `service_name` varchar(255) NOT NULL PRIMARY KEY,  
  `port_number` varchar(255) NULL, 
  `result_code` varchar(3) NOT NULL, 
  `participant_feedback` longtext NOT NULL, 
  `staff_feedback` longtext NOT NULL, 
  `points_obtained` integer NOT NULL, 
  `target_id` integer NULL);
--
-- Add field team to targets
--
ALTER TABLE `targets` ADD COLUMN `team_id` integer NULL , ADD CONSTRAINT `targets_team_id_d1f7c2b6_fk_teams_team_id` FOREIGN KEY (`team_id`) REFERENCES `teams`(`team_id`);
ALTER TABLE `ports` ADD CONSTRAINT `ports_target_id_3fe4af15_fk_targets_target_id` FOREIGN KEY (`target_id`) REFERENCES `targets` (`target_id`);
