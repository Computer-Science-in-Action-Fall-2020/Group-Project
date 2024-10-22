import mysql.connector
from mysql.connector import Error
#This file contains functions to save and receive data from the sql database using mysql.
def connect(host, name, password, db):
    connection = None
    try:
        connection = mysql.connector.connect(host= host, user=name, passwd=password, database=db)
    except Error as err:
        print(f"Error: '{err}'")
    return connection

def ExecuteQuery(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
            cursor.close()
            return result
        else:
            connection.commit()
        print("Query successful")
        cursor.close()
    except Error as err:
        print(f"Query unsuccessful: '{err}'")
#Each save function will create a new row of data in the database for the relevant table.
def SaveForm(FormID, CaseNumber, SubmittingOfficer, Date, Location):
    #Disposed is a TinyInt is which is used as a boolean to tell wether the final disposition has occured.
    #I will most likely create a 5th table for disposition information to keep the database clean.
    query = f'''INSERT INTO `db`.`forms` (`FormID`, `CaseNumber`, `SubmittingOfficer`, `Date`, `Location`, `Disposed`) 
                VALUES ({FormID}, {CaseNumber}, '{SubmittingOfficer}', '{Date}', '{Location}', 0);'''
    return query

def SaveItem(ItemID, FormID, Item):
    #Forms can have multiple pieces of evidence so the FormID is used to group all of them together.
    query = f'''INSERT INTO `db`.`items` (`ItemID`, `FormID`, `Item`) 
                VALUES ({ItemID}, {FormID}, '{Item}');'''
    return query
def SaveChange(ChangeID, FormID, ReleasedBy, ReceivedBy, Purpose, Location, ReleaseSignature, ReceiptSignature):
    #FormID is used in the same way here as it is in the SaveItem function. Each time a change is saved, a new hash should be also created.
    query = f'''INSERT INTO `db`.`changelog` (`ChangeID`, `FormID`, `ReleasedBy`, `ReceivedBy`, `Purpose`, `Location`, `ReleaseSignature`, `ReceiptSignature`)
                Values({ChangeID}, {FormID}, '{ReleasedBy}', '{ReceivedBy}', '{Purpose}', '{Location}', '{ReleaseSignature}', '{ReceiptSignature}');'''
    return query

def SaveHash(FormID, ChangeID, Hash, FinalHash):
    #Hashing hasn't been implemented yet but a hash code will be generated for each change made to the form and saved in the hash table.
    #ChangeID will be used to save when the change was made and the FormID is for which form was made.
    #FinalHash was intended to be generated after the final disposition but doesn't seem like it will be necessary.
    query = f'''INSERT INTO `db`.`changelog` (`FormID`, `ChangeID`, `Hash`, `FinalHash`)
                Values({FormID}, {ChangeID}, '{Hash}', {FinalHash})'''
    return query
#GetItems and GetChanges are helper functions for the GetFormInfo function.
def GetItems(connection, FormID):
    items = []
    query = f''' SELECT *
                FROM `items`
                WHERE `FormID` = {FormID}
                '''
    for item in ExecuteQuery(connection, query):
        ID, Form, Item = item
        items.append({"ItemID": ID,"FormID": Form, "Item": Item})
    return items

def GetChanges(connection,FormID):
    changes = []
    query = f''' SELECT *
                 FROM `changelog`
                 WHERE `FormID` = {FormID}'''
    for change in ExecuteQuery(connection, query):
        ID, Form, ReleasedBy, ReceivedBy, Purpose, Location, ReleaseSignature, ReceiptSignature = change
        changes.append({"ChangeID": ID,
                        "FormID": Form,
                        "ReleasedBy": ReleasedBy,
                        "ReceivedBy": ReceivedBy,
                        "Purpose": Purpose,
                        "location": Location,
                        "ReleaseSignature": ReleaseSignature,
                        "ReceiptSignature": ReceiptSignature})
    return changes
#GetFormInfo returns a dictionary of all the relevant information (aside from hashes those will be added when it's implemented)
#The "Items" and "Changes" values will be a list of dictionaries containing all the information for each item or change.
def GetFormInfo(connection, FormID):
    query = f'''SELECT `CaseNumber`, `SubmittingOfficer`, `Date`, `Location`
                    FROM `Forms`
                    WHERE `FormID` = {FormID}'''
    CaseNumber, SubmittingOfficer, Date, Location = ExecuteQuery(connection, query)[0]

    FormInfo = {"FormID": FormID,
                "CaseNumber": CaseNumber,
                "SubmittingOfficer": SubmittingOfficer,
                "Date": Date,
                "Location": Location,
                "Items": GetItems(connection, FormID),
                "Changes": GetChanges(connection, FormID)}
    return FormInfo
