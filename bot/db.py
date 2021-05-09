import sqlite3
import os
import sys
import datetime

cwd = os.path.dirname(os.path.abspath(__file__))
sep = "/"

if str(sys.platform) in ["win32", "cygwin", "msys"]:
    sep = "\\"


def loadDB():
    dump_data = True
    if os.path.isfile(cwd + sep + 'db.sqlite'):
        # os.remove(cwd + sep + 'db.sqlite')
        dump_data = False

    conn = sqlite3.connect(cwd + sep + 'db.sqlite')
    cur = conn.cursor()
    conn.text_factory = str

    cur.executescript('''
    CREATE TABLE IF NOT EXISTS questions
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
     question TEXT, 
     author TEXT)
    ''')

    cur.executescript('''
    CREATE TABLE IF NOT EXISTS answers
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
     questionID INTEGER,
     answer TEXT)
    ''')

    cur.executescript('''
    CREATE TABLE IF NOT EXISTS claims
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
     company_id TEXT, 
     name TEXT,
     amount INTEGER,
     filename TEXT,
     date TEXT,
     reimbursed INTEGER)
    ''')

    cur.executescript('''
    CREATE TABLE IF NOT EXISTS applications
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
     author TEXT,
     email TEXT,
     phone INTEGER,
     jobID INTEGER,
     filename TEXT,
     date TEXT)
    ''')

    cur.executescript('''
    CREATE TABLE IF NOT EXISTS commitments
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
     title TEXT);
    ''')

    cur.executescript('''
    CREATE TABLE IF NOT EXISTS jobs
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
     title TEXT,
     date TEXT,
     commitment INTEGER,
     remote INTEGER,
     DESCRIPTION TEXT,
     FOREIGN KEY(commitment) REFERENCES commitments (id))
    ''')

    if dump_data is True:
        cur.executescript('''
        INSERT INTO questions
        (question, author)
        VALUES
        ('What is the purpose of this bot?', 'Default Question')
        ''')
        cur.executescript('''
        INSERT INTO questions
        (question, author)
        VALUES
        ('What are the functions of this bot?', 'Default Question')
        ''')
        cur.executescript('''
        INSERT INTO questions
        (question, author)
        VALUES
        ('What language was used to create this bot?', 'Default Question')
        ''')
        cur.executescript('''
        INSERT INTO questions
        (question, author)
        VALUES
        ('Who are the people behind this amazing bot', 'Default Question')
        ''')
        cur.executescript('''
        INSERT INTO questions
        (question, author)
        VALUES
        ('Why was this bot created?', 'Default Question')
        ''')

        cur.executescript('''
        INSERT INTO answers
        (questionID, answer)
        VALUES
        (1, 'To help HR personnel/HR Department in some of their day-to-day operations')
        ''')
        cur.executescript('''
        INSERT INTO answers
        (questionID, answer)
        VALUES
        (2, 'This bot is able to: Smoothen and quicken the process of job application, Give a quick overview and run-through of the organization (its structure, layout, mission, vision etc.), Handle and answers frequently asked questions (FAQs) by employees and members of the public, and create a no-fuss process of submitting claims by employees')
        ''')
        cur.executescript('''
        INSERT INTO answers
        (questionID, answer)
        VALUES
        (3, 'English language! Hehe just kidding... Python! :)')
        ''')
        cur.executescript('''
        INSERT INTO answers
        (questionID, answer)
        VALUES
        (5, 'This was created as part of our AB0403 project diving into creating a product with python, to test our limits and have fun!')
        ''')
        cur.executescript('''
        INSERT INTO commitments
        (title)
        VALUES
        ('Internship')
        ''')
        cur.executescript('''
        INSERT INTO commitments
        (title)
        VALUES
        ('Part-Time')
        ''')
        cur.executescript('''
        INSERT INTO commitments
        (title)
        VALUES
        ('Full-Time')
        ''')
        cur.executescript('''
        INSERT INTO commitments
        (title)
        VALUES
        ('Freelance')
        ''')

        cur.executescript('''
        INSERT INTO jobs
        (title, date, commitment, remote, description)
        VALUES
        ('Software Engineer', '2020-12-05', 1, 0,
        "The role also covers writing diagnostic programs and designing and writing code for operating systems and software to ensure efficiency. When required, you'll make recommendations for future developments.")
        ''')
        cur.executescript('''
        INSERT INTO jobs
        (title, date, commitment, remote, description)
        VALUES
        ('Account Manager', '2019-04-12', 3, 0,
        "Generate sales among client accounts, including upsetting and cross-selling. Operates as the point of contact for assigned customers. Develops and maintains long-term relationships with accounts. Makes sure clients receive requested products and services in a timely fashion.")
        ''')
        cur.executescript('''
        INSERT INTO jobs
        (title, date, commitment, remote, description)
        VALUES
        ('Graphic Designer', '2020-01-12', 4, 1,
        "Working with clients, briefing and advising them with regard to design style, format, print production and timescales. developing concepts, graphics and layouts for product illustrations company logos and websites. determining size and arrangement of copy and illustrative material as well as font style and size.")
        ''')
        cur.executescript('''
        INSERT INTO applications
        (author, email, phone, filename, jobID, date)
        VALUES
        ('Alan', 'alan@gmail.com', 11111111, 'Alan Resume.pdf', 3, "2021-01-05 20:46:26.860521")
        ''')
        cur.executescript('''
        INSERT INTO applications
        (author, email, phone, filename, jobID, date)
        VALUES
        ('Bob', 'bob@gmail.com', 222222222, 'Bob Resume.pdf', 3, "2021-01-12 20:46:26.860521")
        ''')
        cur.executescript('''
        INSERT INTO applications
        (author, email, phone, filename, jobID, date)
        VALUES
        ('Charlie', 'charlie@gmail.com', 33333333, 'Charlie Resume.pdf', 3, "2021-01-03 20:46:26.860521")
        ''')
        cur.executescript('''
        INSERT INTO applications
        (author, email, phone, filename, jobID, date)
        VALUES
        ('Eden','eden@gmail.com', 44444444, 'Eden Resume.pdf', 1, "2020-12-17 20:46:26.860521")
        ''')
        cur.executescript('''
        INSERT INTO applications
        (author, email, phone, filename, jobID, date)
        VALUES
        ('Falcon','falcon@gmail.com', 5555555, 'Falcon Resume.pdf', 2, "2020-12-30 20:46:26.860521")
        ''')
        cur.executescript('''
        INSERT INTO applications
        (author, email, phone, filename, jobID, date)
        VALUES
        ('George','george@gmail.com', 66666666, 'George Resume.pdf', 1, "2021-01-01 20:46:26.860521")
        ''')

        cur.executescript('''
        INSERT INTO claims
        (company_id, name, amount, filename, date, reimbursed)
        VALUES
        ('EMP0001', 'Employee #1', 101.38, 'Employee #1 Proof.pdf', "2020-12-18 20:46:26.860521", 0)
        ''')
        cur.executescript('''
        INSERT INTO claims
        (company_id, name, amount, filename, date, reimbursed)
        VALUES
        ('EMP0002', 'Employee #2', 56.11, 'Employee #2 Proof.pdf', "2020-11-18 20:46:26.860521", 0)
        ''')
        cur.executescript('''
        INSERT INTO claims
        (company_id, name, amount, filename, date, reimbursed)
        VALUES
        ('EMP0003', 'Employee #3', 121.01, 'Employee #3 Proof.pdf', "2020-10-18 20:46:26.860521", 0)
        ''')
        cur.executescript('''
        INSERT INTO claims
        (company_id, name, amount, filename, date, reimbursed)
        VALUES
        ('EMP0004', 'Employee #4', 10.07, 'Employee #4 Proof.pdf', "2019-10-18 20:46:26.860521", 1)
        ''')

    conn.commit()
    conn.close()


def getAvailablePositions():
    conn = sqlite3.connect(cwd + sep + 'db.sqlite')
    cur = conn.cursor()
    conn.text_factory = str

    return cur.execute('''
    SELECT jobs.id, jobs.title, commitments.title
    FROM jobs INNER JOIN commitments on jobs.commitment = commitments.id''')


def getQuestionsAndAnswers():
    conn = sqlite3.connect(cwd + sep + 'db.sqlite')
    cur = conn.cursor()
    conn.text_factory = str

    return cur.execute('''
    SELECT questions.question, answers.answer
    FROM questions INNER JOIN answers on questions.id = answers.questionID''')


def addJobApplication(author, email, phone, filename, job):
    conn = sqlite3.connect(cwd + sep + 'db.sqlite')
    cur = conn.cursor()
    conn.text_factory = str

    cur.execute("INSERT INTO applications (author, email, phone, filename, date, jobID) VALUES (?, ?, ?, ?, ?, ?)",
                (author, email, phone, filename, str(datetime.datetime.now()), job))

    conn.commit()
    conn.close()


def addClaim(company_id, name, amount, filename):
    conn = sqlite3.connect(cwd + sep + 'db.sqlite')
    cur = conn.cursor()
    conn.text_factory = str

    cur.execute("INSERT INTO claims (company_id, name, amount, filename, date, reimbursed) VALUES (?, ?, ?, ?, ?, ?)",
                (company_id, name, amount, filename, str(datetime.datetime.now()), 0))

    conn.commit()
    conn.close()


def addQuestion(name, question):
    conn = sqlite3.connect(cwd + sep + 'db.sqlite')
    cur = conn.cursor()
    conn.text_factory = str

    cur.execute("INSERT INTO questions (author, question) VALUES (?, ?)",
                (name, question))

    conn.commit()
    conn.close()


def loadQuery():
    conn = sqlite3.connect(cwd + sep + 'db.sqlite')
    cur = conn.cursor()
    conn.text_factory = str

    print("Printing Commitment Types...")
    for row in cur.execute("SELECT * FROM commitments"):
        print(row)
    print()

    print("Printing Jobs...")
    for row in cur.execute("SELECT * FROM jobs"):
        print(row)
    print()

    print("Printing Job Applications...")
    for row in cur.execute("SELECT * FROM applications"):
        print(row)
    print()

    print("Printing Job Applications with specified commitment...")
    for row in cur.execute("SELECT applications.*, jobs.title, commitments.title FROM applications " +
                           "INNER JOIN jobs ON applications.jobID = jobs.id INNER JOIN commitments ON "
                           "jobs.commitment = commitments.id"):
        print(row)
    print()

    print("Printing Claims...")
    for row in cur.execute("SELECT * FROM claims"):
        print(row)
    print()

    print("Printing Questions...")
    for row in cur.execute("SELECT * FROM questions"):
        print(row)
    print()

    print("Printing Answers...")
    for row in cur.execute("SELECT * FROM answers"):
        print(row)
    print()
