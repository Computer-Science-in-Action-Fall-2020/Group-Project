import mysql.connector
from mysql.connector import Error
import argparse

#This file is meant to be ran once to set up the sql database.
#It's meant to be executed from your CLI with the command: python SetupDB.py --host <host> --user <yourusername> --password <yourpassword> --database <nameofdatabase>
#If there is no database by your inputed name a new one will be created, if there's already one, the tables will be added to the pre-existing database.
#right now 4 tables will be created for Forms, Items, Changes, and Hashes, but a 5th will probably be needed for disposition info.

def SetupDB(cursor):
    query = """
        CREATE TABLE `Forms` (
            `RowID` int NOT NULL AUTO_INCREMENT,
            `FormID` int NOT NULL,
            `CaseNumber` int NOT NULL,
            `SubmittingOfficer` VARCHAR(255) NOT NULL,
            `Date` VARCHAR(50) NOT NULL,
            `Location` VARCHAR(255) NOT NULL,
            `Disposed` TINYINT(1) NOT NULL,
            `DispositionDate` VARCHAR(50) NULL,
            `DispositionAuth` VARCHAR(255) NULL,
            PRIMARY KEY (`RowID`));
             
        CREATE TABLE `changelog` (
            `ChangeID` int NOT NULL AUTO_INCREMENT,
            `FormID` int NOT NULL,
            `ReleasedBy` VARCHAR(255) NOT NULL,
            `ReceivedBy` VARCHAR(255) NOT NULL,
            `Purpose` VARCHAR(255) NOT NULL,
            `Location` VARCHAR(255) NOT NULL,
            `ReleaseSignature` VARCHAR(255) NOT NULL,
            `ReceiptSignature` VARCHAR(255) NOT NULL,
            PRIMARY KEY (`ChangeID`));

        CREATE TABLE `Hashes` (
            `FormID` int NOT NULL,
            `ChangeID` int NOT NULL,
            `Hash` VARCHAR(255) NOT NULL,
            `FinalHash` tinyint(1) NOT NULL,
            PRIMARY KEY (`FormID`, `ChangeID`));

        CREATE TABLE `Items` (
            `ItemID` int NOT NULL AUTO_INCREMENT,
            `FormID` int NOT NULL,
            `Item` VARCHAR(255) NOT NULL,
            PRIMARY KEY (`ItemID`));

        ALTER TABLE `changelog` ADD CONSTRAINT `fk_changelog_FormID` FOREIGN KEY(`FormID`)
        REFERENCES `Forms` (`FormID`);

        ALTER TABLE `Hashes` ADD CONSTRAINT `fk_Hashes_FormID` FOREIGN KEY(`FormID`)
        REFERENCES `Forms` (`FormID`);

        ALTER TABLE `Hashes` ADD CONSTRAINT `fk_Hashes_ChangeID` FOREIGN KEY(`ChangeID`)
        REFERENCES `changelog` (`ChangeID`);

        ALTER TABLE `Items` ADD CONSTRAINT `fk_Items_FormID` FOREIGN KEY(`FormID`)
        REFERENCES `Forms` (`FormID`);"""
    cursor.execute(query)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Setup the database.")
    parser.add_argument('--host', required=True, help="Database host")
    parser.add_argument('--user', required=True, help="Database username")
    parser.add_argument('--password', required=True, help="Database password")
    parser.add_argument('--database', required=True, help="Database name")

    args = parser.parse_args()

    # Connect to the database
    try:
        connection = mysql.connector.connect(host=args.host, user=args.user, password=args.password)
        query = f'CREATE DATABASE IF NOT EXISTS `{args.database}`'
        cursor = connection.cursor()
        cursor.execute(query)
        connection.database = args.database
        SetupDB(cursor)

    except Error as err:
        print(f'connection failed: {err}')


