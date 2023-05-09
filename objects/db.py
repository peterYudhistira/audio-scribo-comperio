import sqlite3
import pandas as pd
import os


class DatabaseHandler():
    def __init__(self, dbName):
        self.cursor = sqlite3.connect(dbName)
        self.create_tables()

    # create
    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS speakers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT NOT NULL
            );
        """)

        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                datetime TEXT NOT NULL
            );
        """)

        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS record_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                speaker_id INTEGER,
                question_text NOT NULL,
                transcript_audio TEXT NOT NULL,
                transcript_text TEXT NOT NULL
            );
        """)

    def create_speaker(self, speakerName, speakerCode):
        self.cursor.execute("""
                INSERT INTO speakers (name, code)
                VALUES (?, ?)        
        """, (speakerName, speakerCode))
        self.cursor.commit()

    def create_event(self, eventTitle, eventDate):
        id = self.cursor.execute("""
                INSERT INTO events (title, datetime)
                VALUES (?, ?)
        """, (eventTitle, eventDate)).lastrowid
        self.cursor.commit()
        print("Current event is at {}".format(id))

        # create the directory.
        os.mkdir("records/event{}".format(id))

    def create_record_audio(self, event_id, speaker_id, question, audio_path):
        self.cursor.execute("""
                INSERT INTO record_data (event_id, speaker_id, question_text, transcript_audio, transcript_text)
                VALUES (?, ?, ?, ?, "")
        """, (event_id, speaker_id, question, audio_path))
        self.cursor.commit()

    def create_record_text(self, event_id, speaker_id, question, text):
        self.cursor.execute("""
                INSERT INTO record_data (event_id, speaker_id, question_text, transcript_audio, transcript_text)
                VALUES (?, ?, ?, "", ?)
        """, (event_id, speaker_id, question, text))
        self.cursor.commit()

    # read
    def get_speaker(self, selector, ID):
        return self.cursor.execute("""
                SELECT * FROM speakers 
                WHERE {} = ?
        """.format(selector), (ID,)).fetchone()

    def get_event(self, selector,  ID):
        return self.cursor.execute("""
                SELECT * FROM events
                WHERE {} = ?
        """.format(selector), (ID,)).fetchone()

    def get_recordData(self, selector, ID):
        query = """
                SELECT * FROM record_data
                WHERE {} = ?
        """.format(selector)
        self.cursor.execute(query, (ID,)).fetchall()

    # list

    def list_speakers(self):
        return self.cursor.execute("""
                SELECT * FROM speakers
        """).fetchall()

    def list_events(self):
        return self.cursor.execute("""
                SELECT * FROM events
        """).fetchall()

    def list_recordData(self):
        return self.cursor.execute("""
                SELECT * FROM record_data
        """).fetchall()

    # definitive record data
    def list_recordData_complete(self):
        pass

    # update
    def update_recordData_text(self, ID, text):
        self.cursor.execute("""
                UPDATE record_data
                SET text = ?
                WHERE id = ?
        """, (text, ID))
        self.cursor.commit()

    # delete
    def clear_table(self, table):
        self.cursor.execute("""
                DELETE FROM {};
        """.format(table))
        self.cursor.commit()

    # goofy ahh functions
    def get_recordCountByEventID(self, eventID):
        return len(self.get_recordData("event_id", eventID))

    def loop_create_speaker(self):
        # # create speakers
        while True:
            name = input("Name : ")
            if name == "stop":
                break
            code = input("Code : ")
            self.create_speaker(name, code)

    def create_recordDataFromExcel(self, filePath, sheetName, eventID):
        df = pd.read_excel(filePath, sheet_name=sheetName)
        for i in df.index:
            print("-" * 80)
            speakerCode = df.loc[i]["Speaker"]
            print(speakerCode)
            speakerData = self.get_speaker("code", speakerCode)
            speakerID = speakerData[0]

            self.create_record_text(event_id=eventID, speaker_id=speakerID, question=df.loc[i]["Question"], text=df.loc[i]["Answer"])
            print("-" * 80)
            
    def get_recordDataJoined(self, selector, ID):
        query = """
                SELECT record_data.id as id, events.title as event_title, events.datetime as date, speakers.code as speaker_code, question_text, transcript_audio, transcript_text
                FROM record_data
                INNER JOIN events
                ON record_data.event_id = events.id
                INNER JOIN speakers
                ON record_data.speaker_id = speakers.id
                WHERE record_data.{} = ?
        """.format(selector)
        return self.cursor.execute(query, (ID,)).fetchall()
    
    def get_recordDataJoinedDF(self, selector, ID):
        query = """
                SELECT record_data.id as id, events.title as event_title, speakers.code as speaker, question_text as question, transcript_text as answer
                FROM record_data
                INNER JOIN events
                ON record_data.event_id = events.id
                INNER JOIN speakers
                ON record_data.speaker_id = speakers.id
                WHERE record_data.{} = {}
        """.format(selector, ID)
        df = pd.read_sql_query(query, self.cursor)
        return df


# dh = DatabaseHandler("database/testdb.db")
# dh.clear_table("record_data")
# dh.create_recordDataFromExcel("database/raws/Dataset.xlsx", "19-Feb", 18)
# dh.create_recordDataFromExcel("database/raws/Dataset.xlsx", "26-Feb", 19)
# dh.create_recordDataFromExcel("database/raws/Dataset.xlsx", "2-Jul", 20)
# print(dh.get_recordDataJoined("event_id", 10))
# print(dh.get_recordData("event_id", 11))
