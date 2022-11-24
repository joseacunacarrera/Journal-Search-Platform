-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8mb3 ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `mydb`.`jobs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`jobs` (
  `id` INT(11) NOT NULL,
  `created` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `status` VARCHAR(45) NULL DEFAULT NULL,
  `end` DATETIME NULL DEFAULT NULL,
  `loader` VARCHAR(45) NULL DEFAULT NULL,
  `grp_size` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb`.`groups`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`groups` (
  `id` INT(11) NOT NULL,
  `created` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `end` DATETIME NULL DEFAULT NULL,
  `stage` VARCHAR(45) NULL DEFAULT NULL,
  `grp_number` INT(11) NULL DEFAULT NULL,
  `status` VARCHAR(45) NULL DEFAULT NULL,
  `offset` INT(11) NULL DEFAULT NULL,
  `id_job` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_groups_jobs_idx` (`id_job` ASC) VISIBLE,
  CONSTRAINT `fk_groups_jobs`
    FOREIGN KEY (`id_job`)
    REFERENCES `mydb`.`jobs` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb`.`history`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`history` (
  `id` INT(11) NOT NULL,
  `component` VARCHAR(45) NULL DEFAULT NULL,
  `status` VARCHAR(45) NULL DEFAULT NULL,
  `created` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `end` DATETIME NULL DEFAULT NULL,
  `message` TEXT NULL DEFAULT NULL,
  `stage` VARCHAR(45) NULL DEFAULT NULL,
  `grp_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_history_groups1_idx` (`grp_id` ASC) VISIBLE,
  CONSTRAINT `fk_history_groups1`
    FOREIGN KEY (`grp_id`)
    REFERENCES `mydb`.`groups` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
