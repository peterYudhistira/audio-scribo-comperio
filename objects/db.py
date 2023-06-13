import sqlite3
import pandas as pd
import os


class DatabaseHandler():
    def __init__(self, dbName, keepSchema: bool = True):
        self.cursor = sqlite3.connect(dbName)
        if not keepSchema:
            print('ya schema empty, yeet')
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
        # self.cursor.execute("DROP TABLE record_data") # the sacred seal of the nine tails. Do not open
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS record_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                speaker_id INTEGER,
                question_text NOT NULL,
                transcript_audio TEXT NOT NULL,
                transcript_text TEXT NOT NULL,
                transcribe_lang TEXT NOT NULL
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

    def create_record_audio(self, event_id, speaker_id, question, audio_path, transcribe_lang):
        self.cursor.execute("""
                INSERT INTO record_data (event_id, speaker_id, question_text, transcript_audio, transcript_text, transcribe_lang)
                VALUES (?, ?, ?, ?, "", ?)
        """, (event_id, speaker_id, question, audio_path, transcribe_lang))
        self.cursor.commit()

    def create_record_text(self, event_id, speaker_id, question, text):
        self.cursor.execute("""
                INSERT INTO record_data (event_id, speaker_id, question_text, transcript_audio, transcript_text, transcribe_lang)
                VALUES (?, ?, ?, "", ?, "")
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

    # update
    def update_recordData_text(self, ID, text):
        self.cursor.execute("""
                UPDATE record_data
                SET transcript_text = ?
                WHERE id = ?
        """, (text, ID))
        self.cursor.commit()

    # delete
    def clear_table(self, table):
        self.cursor.execute("""
                DELETE FROM {};
        """.format(table))
        self.cursor.commit()

    def delete_by_id(self, table:str, id:int):
        self.cursor.execute("""
            DELETE FROM {}
            WHERE ID = ?
        """.format(table), (id,))
        self.cursor.commit()

    # goofy ahh functions
    def loop_create_speaker(self):
        # # create speakers
        while True:
            name = input("Name : ")
            if name == "stop":
                break
            code = input("Code : ")
            self.create_speaker(name, code)


    def get_recordDataJoined(self, selector, ID):
        query = """
                SELECT record_data.id as id, events.title as event_title, events.datetime as date, speakers.code as speaker_code, question_text, transcript_audio, transcript_text, transcribe_lang
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
# dh.delete_by_id("record_data", 75)
# dh.delete_by_id("record_data", 76)
# dh.delete_by_id("record_data", 77)
# dh.delete_by_id("record_data", 78)
# dh.delete_by_id("record_data", 97)
# dh.update_recordData_text(2,"We came from evolution. This is undeniable, and the Charles Darwin's evolution model is the most widely accepted theory to this. We evolved from unicellular bacteriae, to fish, to amphibious creatures, to mammals, to apes, then all the way to humans.")
# dh.update_recordData_text(119, "OK, thank you ko. Yeah, i wanted to communicate that, but my words are missing. So for example computer, i have screen here, i have CPU here, they are limited by the components. For example, my screen is 21 inches, and RGB something. And my CPU, the spec is, the RAM is 16 giga, and the GPU is RTX, or GTX, i forget. And this computer is limited by those rooms, those scopes, so that it cannot get out of those scopes. My screen can't just shrink to 15 inches, or get big to 40 inches. CPU cannot go up to 32 giga, and GTX cannot go up to RTX. Cannot, unless i change it myself. Unless, that which is outside the limits make intervention and change what is within the limits.")
# dh.update_recordData_text(120, "As a person who follows post-modernism, yeah, post-modernism is a little troublesome. To me, yeah, hierarchy is determined by humans, isn't it? We categorize by ourself, like soup A 1, soup A 2, this atmosphere, atmosphere A B C, this and that dimension, such is human. Well me, because i am a post-modernist, i think that what if humans think like that because that is all we know. Maybe it is askew from reality. One day maybe atmosphere will turn out to have 30 layers, not 7. We do not know. We can only search and search. About hierarchy, it may exist, but not certain. I think this because, if you know, i see the story of Warhammer 40k. Turns out there is cosmic dimension that makes them able to cross dimensions. But then they meet Chaos gods. Turns out the god they worship is atheist, actually. Just a man that is powerful. From there i learn that it may be that we are being lied to. The famous social philosophy is everything is illusion. But Peter is right, i guess. For instance Artificial intelligence, it works because of the data that we give, photos that we give, footages that we give. Imagine if god makes it like that, that what if god makes us think that he is like that, while he isn't. Just like a paradox, i forget, about the creation. I don't know the exact answer. It is mysterious, one of the world's mysteriousness.")
# dh.update_recordData_text(121, "Uh, the limits are bound by humans, that it is imaginary. For me, perhaps, maybe, i attribute it to human limitation, because of human's limitations of understanding. Because it is not something that humans are meant to understand, that the limitations are there and absolute. But, there are things that are beneath us. For instance, about programming, hierarchy is absolute. User is beyond everything, and below user is a program, and below program is a language, and below language is the binary, that is the bits and 0 1 0 1. In the hierarchy that is below us, i can bear witness, i can vouch that that which is below cannot influence that which is above. So i feel sufficiently confident to think that there are limitations above me that i cannot comprehend fully, that i cannot transcend. And above it, there is another, and another, until there is a scope that transcends everything, the whole universe.")
# dh.update_recordData_text(122, "I believe that, what is it, based on what i see below me, that cannot interact with me above it, there exists limitations. Like this, humans want a lot of things, but program does not understand what human wants, so the media between human and program exists, that is the programming language. I cannot make a program that understands human emotions, because, yeah, it is hard to communicate it to program. That is why, i believe that there is a principle above us, that we cannot understand, that i cannot comprehend. To me, this universal principle, i believe that it is god. This is what i believe as a person with religion. This is based on what is within scope cannot comprehend that which is outside the scope. I cannot understand the principles of life, why gravity, laws of nature, and physics are like that, i don't understand. I do not understand that which is outside of my scope, unless that which is outside of the scope explains to me in a language that i understand. That it makes contact with me willingly, with, say, writings, words, yeah, or something that i can see and understand. Oh, so it is like that.")
# dh.update_recordData_text(123, "The counter, that is, i found on TikTok, that everything is illusion. It's all in our heads. All that we speak of is illusion. A philosopher said that we are living in a dream, in a hologram, in a simulation. So we have been talking like we are smoking weed. Also, it doesn't mean that when we find a hierarchy, that it really is a hierarchy, or that there is god. Because Peter said about artificial intelligence, if a person's brain is put inside an artificial intelligence, it could be that his arguments are revolving, in a paradox. Who is creating who, who is creating God, it could be like that. The point is it is mysterious. Even though i am Christian and cannot think like that, that it is heretical. But the world is vast, so now we can think such and so. People can be more open minded, the science is advanced, and now we know about how consciousness works. So, i see on TikTok, that when a person dies, there is a brain, right, if the brain is preserved and taken care of, the brain can be alive again, as long as it is not rotting. It lives again. So imagine that your brain is revived, but with no body. Imagine that, and now we know how consciousness works. We know how brain and biology works. But essence, we have no milestone. Otherwise the paradox begins again, like Big Bang, when it happens, whether God is there or not. So i don't know, it just revolves like that.")
# dh.update_recordData_text(124, "If we say between knowing and not, basically, in the end, we only know what we know. We only know what we know. Yeah. Outside of that, we don't know. I heard that somewhere, whatever. So, we only know what we know. For me, for me, we can know how does what is above us work, for example time. We know how time works, we know it flows. There is flow of time, that we know. We know that the world of physics, it works in dimensional ways. We have 3 dimensions, and so on. I don't understand that fully, but the point is, we can be aware of something is above us. But i know that time is outside of our scope, because we cannot create time. We cannot create in quote, a dimension. We can live in a dimension, or create things in a dimension, but we cannot create a dimension. Or we cannot create time. So time and dimension is higher in the hierarchy. But we know how it works. So, in the end, we can know that which is above us, but only that. We cannot understand it, never know.")
# dh.update_recordData_text(125, "Because, as Samuel Sugiarto says, the theology professor of Petra, that humans are below humans. Which is, that is his belief, yeah. This is small intermezzo, for his genre of Christianity, it is below him. We did not create animals, yeah, Peter, but the majority think that animals are below them. Ko cep always says that animals are below us, does not have free will, or consciousness like us, et cetera. But it turns out recent studies prove that animals are like humans, but just less skillful in it. For example, animals like sex. Turns out not only humans like sex. Animals like sex too, for example. The primates find certain movements that can be enjoyed sexually. Cats and dogs are too. In certain degree, animals are exactly like humans. Animals like violence, even ants fight each other because of different skin color. Not even artificial intelligence, even animals that are below us are not different from us. Only different in shape, but same in principle. I question what should i believe now, because if i believe Mr Samuel, animals are within control. But as i read, animals are not within control. Maybe god is like that, maybe god cannot be read as such. No, no, that is bad. The point is, the more we know, turns out, the more we don't know. It could be that we know God, but in that, we don't know him even more.")
