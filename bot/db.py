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
        ('How do i request for vacation time?', 'Default Question')
        ''')
        cur.executescript('''
        INSERT INTO questions
        (question, author)
        VALUES
        ('How do i get information about my benefits?', 'Default Question')
        ''')
        cur.executescript('''
        INSERT INTO questions
        (question, author)
        VALUES
        ('How do i report a hazard in the workplace?', 'Default Question')
        ''')
        cur.executescript('''
        INSERT INTO questions
        (question, author)
        VALUES
        ('Can a supervisor mandate work arrangements for an entire unit or department?', 'Default Question')
        ''')

        cur.executescript('''
        INSERT INTO answers
        (questionID, answer)
        VALUES
        (1, 'If there are some specific dates you are interested in taking for vacation, speak to your immediate supervisor.')
        ''')
        cur.executescript('''
        INSERT INTO answers
        (questionID, answer)
        VALUES
        (2, 'In order to view your current benefit plan details, you can go to the ‘Employee Services’ section on our website and view ‘Benefits and Deductions’.')
        ''')
        cur.executescript('''
        INSERT INTO answers
        (questionID, answer)
        VALUES
        (3, 'It is the worker’s responsibility to report any workplace hazards to their immediate supervisors. A hazard is defined as any practice, behaviour, condition, thing, situation, or a combination of these things, having the potential to cause injury or illness to a person or damage to property or equipment.')
        ''')
        cur.executescript('''
        INSERT INTO answers
        (questionID, answer)
        VALUES
        (4, 'It is in the supervisor’s interest to consider individual scheduling preferences and to make the best effort to respond to these, to avoid reduced productivity or the challenges and costs of turnover. However, a supervisor may change work schedules and arrangements to accommodate organizational needs.')
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
