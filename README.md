% AIS Project - Test Data
% NPR

## Root directory

Total: 74M

|  Size| File                 |   Description                              | 
|-----:|----------------------|--------------------------------------------| 
|  74M | denmark_tiles.zip    | PNG tiles                                  |
| 116K | sample_input.json    | 500 messages, for unit tests on input data |


## Mongo subfolder:

Total: 72M

|  Size| File                            | Description                                                               | 
|-----:|---------------------------------|---------------------------------------------------------------------------| 
|  28M | aisdk_20201118_1000000.json.zip | 1M messages, for read ops tests                                           |          
|  47M | AISTestData.bson.gz             | Entire test database, in binary form                                      |
|  48K | mapviews.json                   | Tile metadata                                                             |
|  33K | ports.json                      | Port descriptions (only within the geographical area covered by the tiles)|
| 8.5M | vessels.json.zip                | Vessel descriptions                                                       |


### Installation

1. Decompress the `*.json.zip` files
2. Then:

   ~~~~~~~~~~~~~~{.bash}
   mongoimport -d AISTestData -c vessels --maintainInsertionOrder vessels.json
   mongoimport -d AISTestData -c mapviews --maintainInsertionOrder mapviews.json
   mongoimport -d AISTestData -c ports --maintainInsertionOrder ports.json
   mongoimport -d AISTestData -c aisdk_20201118 --maintainInsertionOrder aisdk_20201118_1000000.json
   ~~~~~~~~~~~~~~~~~~~

3. Alternatively, the entire AISTestData database can be created from the BSON archive:

   ~~~~~~~~~~~~~{.bash}
   mongorestore --drop --gzip --archive=AISTestData.bson.gz
   ~~~~~~~~~~~~~~~~~

## SQL subfolder


Total: 36M


|  Size| File                                 |   Description                               | 
|-----:|--------------------------------------|---------------------------------------------| 
| 9.6M | AIS_MESSAGE_1000000_rows.csv.zip     | AIS messages (supertype, 1M)                |
|  15K | MAP_VIEW.csv                         | Tile metadata                               |
|  11K | PORT.csv                             | Ports (Denmark, Sweden, Germany)            |
|  21M | POSITION_REPORT_1000000_rows.csv.zip | Position reports (950,000)                  |
| 1.2M | STATIC_DATA_1000000_rows.csv.zip     | Static Data messags (50,000)                |
| 4.4M | VESSEL.csv.zip                       | Vessel descriptions (200,000)               |
| 160M | AISTestData_dump.mysql               | AISTestData database (with all of the above)|


### Installation

1. Decompress the `*.csv.zip` files
2. Examine the files, and create the schema for the tables (or use/modify an existing one&mdash;see Milestone 3)
3. Place each file in your MySQL data directory: if you followed my installation recommendations, it should be `C:\Users\<name>\MySQLData\AISTestData`
4. Then, _in the MySQL shell client_:

   ~~~~~~~~~~~~{.sqlmysql}
   LOAD DATA INFILE 'VESSEL.csv' INTO TABLE VESSEL COLUMNS TERMINATED BY ',' IGNORE 1 ROWS;
   LOAD DATA INFILE 'MAP_VIEW.csv' INTO TABLE MAP_VIEW COLUMNS TERMINATED BY ',' IGNORE 1 ROWS;
   LOAD DATA INFILE 'PORT.csv' INTO TABLE PORT COLUMNS TERMINATED BY ';' IGNORE 1 ROWS;
   LOAD DATA INFILE 'AIS_MESSAGE_1000000_rows.csv' INTO TABLE AIS_MESSAGE COLUMNS TERMINATED BY ';' IGNORE 1 ROWS;
   LOAD DATA INFILE 'STATIC_DATA_1000000_rows.csv' INTO TABLE STATIC_DATA COLUMNS TERMINATED BY ';' IGNORE 1 ROWS;
   LOAD DATA INFILE 'POSITION_REPORT_1000000_rows.csv' INTO TABLE POSITION_REPORT COLUMNS TERMINATED BY ';' IGNORE 1 ROWS;
   ~~~~~~~~~~~~~~~~~~~~~~~~~~

5. Alternatively, you may deploy the entire `AISTestData` database with the following command, _in the system shell_:

   ~~~~~~~{.bash}
   $ mysql -u <user> -p < AISTestData_dump.mysql
   ~~~~~~~~~~~~

   This will work if you don't plan to modify the data structure. The schema has been given in Milestone 3.


