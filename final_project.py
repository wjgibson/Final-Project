import json
import unittest
import mysql.connector
from mysql.connector import errorcode
import sys

#Replace these with your credentials
username = "wjgib"
password = "Oliver"

class DAO():

    def __init__( self, stub=False ):
        self.is_stub=stub
        self.connection = None

        try:
            self.connection = mysql.connector.connect(host="localhost",user=username,password=password,database="aistestdata")

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Username or Password is incorrect")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

        if not self.connection:
            sys.exit("Connection failed: exiting.")

    def deploy_database(self):
        
        
        
        pass

    def run(self, query):
        """
        Run a query
        :param query: an SQL query
        :type query: str
        :return: the result set as Python list of tuples
        :rtype: list
        """
        mycursor = self.connection.cursor()
        mycursor.execute(query)
        result = mycursor.fetchall()
        mycursor.close()
        
        return result


    def insert_message_batch(self, batch):
        """
        Insert a batch of messages

        :param batch: an array of AIS messages (objects)
        :type batch: list 
        :return: Number of successful insertions
        :rtype: int
        """
        if type(batch) is str:
            print("Incorrect parameter type: should be a list of messages")
            return -1
        if self.is_stub:
            return len(batch)

        inserted = 0
        
        for message in batch:

            if message['MsgType'] == 'position_report':
                report = PositionReport(message)

            if message['MsgType'] == 'static_data':
                report = StaticData(message)

            try:
                query = "insert into AIS_MESSAGE values {};".format( report.to_shared_sql_values() )
                #print(query)
                self.run(query)

                query = "insert into POSITION_REPORT VALUES {};".format( report.to_position_report_sql_values() )
                #print(query)
                self.run(query)

                query = "insert into VESSEL VALUES {};".format(report.to_vessel_sql_values())
                #print(query)
                self.run(query)

                inserted+=1

            except Exception as e:
                print(e)

        return inserted

            



#These classes ONLY extract data from a json file and format it to be inserted into a database.
class Message:

    def __init__(self, msg ):
        
        self.timestamp = msg['Timestamp'][:-1].replace('T',' ')
        self.mmsi = msg['MMSI']
        self.equiptclass = msg['Class']

    def to_shared_sql_values( self ):
        #first "NULL" value is the ID field, which cannot be null. This will change once we use this without the "aistestdata" database
        return "(NULL, '{}', {}, '{}', NULL)".format( self.timestamp, self.mmsi, self.equiptclass )


class PositionReport( Message ):

    def __init__(self, msg):

        super().__init__(msg)

        self.id = None
        self.status = msg['Status']
        self.longitude = msg['Position']['coordinates'][1]
        self.latitude = msg['Position']['coordinates'][0]
        self.rot = msg['RoT'] if 'RoT' in msg else 'NULL'
        self.sog = msg['SoG'] if 'SoG' in msg else 'NULL'
        self.cog = msg['CoG'] if 'CoG' in msg else 'NULL'
        self.heading = msg['Heading'] if 'Heading' in msg else 'NULL'
        
    def to_position_report_sql_values( self ):
        
        if not self.id: # without a valid key, no output
            return None
        return f"({self.id}, '{self.status}', {self.longitude}, {self.latitude}, {self.rot}, {self.sog}, {self.cog}, {self.heading},NULL,NULL,NULL,NULL)"

class StaticData( Message ):

    def __init__(self, msg):

        super().__init__(msg)

        self.IMO = msg['IMO']
        self.name = msg['Name']
        self.vessel_type = msg['VesselType']
        self.length = msg['Length']
        self.breadth = msg['Breadth']

    def to_vessel_sql_values( self ):
        return "('{}',NULL,'{}',NULL,NULL,'{}','{}',NULL,NULL,'{}',NULL,NULL)".format(self.IMO, self.name, self.length, self.breadth, self.vessel_type)


class TMB_test(unittest.TestCase):
    
    tmb = DAO(True)
    
    batch = """[ {\"Timestamp\":\"2020-11-18T00:00:00.000Z\",\"Class\":\"Class A\",\"MMSI\":304858000,\"MsgType\":\"position_report\",\"Position\":{\"type\":\"Point\",\"coordinates\":[55.218332,13.371672]},\"Status\":\"Under way using engine\",\"SoG\":10.8,\"CoG\":94.3,\"Heading\":97},
                {\"Timestamp\":\"2020-11-18T00:00:00.000Z\",\"Class\":\"AtoN\",\"MMSI\":992111840,\"MsgType\":\"static_data\",\"IMO\":\"Unknown\",\"Name\":\"WIND FARM BALTIC1NW\",\"VesselType\":\"Undefined\",\"Length\":60,\"Breadth\":60,\"A\":30,\"B\":30,\"C\":30,\"D\":30},
                {\"Timestamp\":\"2020-11-18T00:00:00.000Z\",\"Class\":\"Class A\",\"MMSI\":219005465,\"MsgType\":\"position_report\",\"Position\":{\"type\":\"Point\",\"coordinates\":[54.572602,11.929218]},\"Status\":\"Under way using engine\",\"RoT\":0,\"SoG\":0,\"CoG\":298.7,\"Heading\":203},
                {\"Timestamp\":\"2020-11-18T00:00:00.000Z\",\"Class\":\"Class A\",\"MMSI\":257961000,\"MsgType\":\"position_report\",\"Position\":{\"type\":\"Point\",\"coordinates\":[55.00316,12.809015]},\"Status\":\"Under way using engine\",\"RoT\":0,\"SoG\":0.2,\"CoG\":225.6,\"Heading\":240},
                {\"Timestamp\":\"2020-11-18T00:00:00.000Z\",\"Class\":\"Class A\",\"MMSI\":376503000,\"MsgType\":\"position_report\",\"Position\":{\"type\":\"Point\",\"coordinates\":[54.519373,11.47914]},\"Status\":\"Under way using engine\",\"RoT\":0,\"SoG\":7.6,\"CoG\":294.4,\"Heading\":290} ]"""

    def test_insert_message_batch_interface_1( self  ):
        """
        Function `insert_message_batch` takes an array of messages as an input.
        """
        array = json.loads( self.batch )
        inserted_count = self.tmb.insert_message_batch( array )
        self.assertTrue( type(inserted_count) is  int and inserted_count >=0) 

    def test_insert_message_batch_interface_2( self  ):
        """
        Function `insert_message_batch` fails nicely if input is still a string
        """ 
        inserted_count = self.tmb.insert_message_batch( self.batch )
        self.assertEqual( inserted_count, -1) 

    def test_insert_message_batch( self  ):
        """
        Function `insert_message_batch` inserts messages in the MySQL table
        """
        tmb = DAO()
        array = json.loads( self.batch )
        inserted_count = tmb.insert_message_batch( array )
        self.assertTrue( type(inserted_count) is  int and inserted_count >=0) 

if __name__ == '__main__':
    unittest.main()