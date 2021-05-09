import logging
import datetime
import os
import pickle

import telegram.ext

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, \
    CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton

import db

from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

cwd = os.path.dirname(os.path.abspath(__file__))
os.chdir(cwd)

TOKEN = "__TOKEN__"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL, PHONE, POSITION, FILE, DISCLOSURES, CONFIRM, SECOND_EMAIL, C_EMAIL, C_PHONE, C_POSITION, C_FILE = range(11)

ID, AMOUNT, RECEIPT, C_ID, C_AMOUNT, C_RECEIPT, CL_CONFIRM = range(11, 18)

NAVIGATION, ADD, C_ADD = range(18, 21)

MISSION, VISION, KEY, LAYOUT, DONE, CONTROL = range(21, 27)

user_email = None
user_phone = None
user_position = None
user_filename = None
user_update_file = None
user_file = None
user_disclosure = None

c_user_email = False
c_user_phone = False
c_user_position = False
c_user_filename = False

cl_id = None
cl_amount = None
cl_receipt = None
cl_update_receipt = None
cl_receipt_name = None

c_cl_id = False
c_cl_amount = False
c_cl_receipt_name = False

em_add = None
c_em_add = False

vt_mission = None
vt_vision = None
vt_layout = None
vt_Key = None

cl_vt_mission = False
cl_vt_vision = False
cl_vt_layout = False
cl_vt_key = False


def start(update, context: CallbackContext):
    get_member = update.message.from_user

    if get_member is None:
        get_member = "user98"
    else:
        get_member = get_member.first_name

    time_now = datetime.datetime.now().time()
    if 0 <= time_now.hour <= 12:
        greeting = "morning "
    elif 12 < time_now.hour <= 18:
        greeting = "afternoon "
    else:
        greeting = "evening "

    menu_keyboard = [
        ["Job Application"],
        ["Digital Onboarding"],
        ["Employee FAQs"],
        ["Submit Claims"],
        ["Exit! Thank you!"]
    ]

    # menu_inline_keyboard = [
    #     [InlineKeyboardButton("Intern Application", callback_data='ia')],
    #     [InlineKeyboardButton("Virtual Tour", callback_data='vt')],
    #     [InlineKeyboardButton("Employee FAQs", callback_data='ef')],
    #     [InlineKeyboardButton("Claim Procedures", callback_data='cp')],
    #     [InlineKeyboardButton("Exit! Thank you!", callback_data='ex')],
    # ]

    # menu_inline_keyboard_reply = InlineKeyboardMarkup(menu_inline_keyboard)

    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

    update.message.reply_text('Good ' + greeting + str(get_member) + "!"
                              + '\nWhat would you like to do today?', reply_markup=menu_markup)


def ia_ask_email(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Enter your email:')
    return EMAIL


def ia_reject_email(update: Update, context: CallbackContext):
    update.message.reply_text('Email entered rejected. Wrong format!')


def ia_ask_phone(update: Update, context: CallbackContext) -> int:
    global user_email
    user_email = update.message.text
    update.message.reply_text('Email entered: <b><u>{email}</u></b>'.format(email=update.message.text),
                              parse_mode=ParseMode.HTML)
    update.message.reply_text('Enter your phone number:')

    return PHONE


def ia_reject_phone(update: Update, context: CallbackContext):
    update.message.reply_text('Phone contact rejected. Wrong format!')


def ia_ask_position(update: Update, context: CallbackContext) -> int:
    global user_phone
    user_phone = update.message.text
    update.message.reply_text('Phone entered: <b><u>{phone}</u></b>'.format(phone=update.message.text),
                              parse_mode=ParseMode.HTML)

    menu_keyboard = []

    for position in db.getAvailablePositions():
        menu_keyboard.append(["JobID{Id}: {Position}, {Type}"
                             .format(Id=position[0], Position=position[1], Type=position[2])])

    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('What role are you applying for?', reply_markup=menu_markup)

    return POSITION


def ia_ask_file(update: Update, context: CallbackContext) -> int:
    global user_position
    user_position = update.message.text
    update.message.reply_text('Position entered: <b><u>{position}</u></b>'.format(position=update.message.text),
                              parse_mode=ParseMode.HTML)

    update.message.reply_text('Upload Resume (include photo):')

    return FILE


def ia_reject_file(update: Update, context: CallbackContext):
    update.message.reply_text('File uploaded rejected. Wrong format!')


def ia_ask_disclosure(update: Update, context: CallbackContext):
    global user_filename
    global user_update_file
    global user_file

    user_filename = update.message.document.file_name

    user_file = context.bot.getFile(update.message.document.file_id)

    user_update_file = update.message.document

    update.message.reply_text('File uploaded: <b><u>{filename}</u></b>'.format(filename=user_filename),
                              parse_mode=ParseMode.HTML)

    menu_keyboard = [
        ["Yes"]
    ]

    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

    update.message.reply_text(
        "<b>PRIVACY STATEMENT</b>\n\nWe reserve the right to make changes to this Privacy Policy at any time and for any reason. We will alert you about any changes by updating the “Last Updated” date of this Privacy Policy. Any changes or modifications will be effective immediately upon posting the updated Privacy Policy on the Site, and you waive the right to receive specific notice of each such change or modification. You are encouraged to periodically review this Privacy Policy to stay informed of updates. You will be deemed to be aware of, will be subject to, and will be deemed to have accepted the changes in any revised Privacy Policy by your continued use of the Site after the date such revised Privacy Policy is posted.\n\n\n\n\n\nPlease press <b>Yes</b> to provide your permission and to recognise that you have read this entire policy",
        parse_mode=ParseMode.HTML,
        reply_markup=menu_markup)

    return DISCLOSURES


def ia_reject_disclosures(update: Update, context: CallbackContext):
    update.message.reply_text('You must enter "Yes"')


def ia_special(update: Update, context: CallbackContext):
    update.message.reply_text('Special REGEX')


def ia_ask_confirm(update: Update, context: CallbackContext):
    global user_disclosure

    global user_email
    global user_phone
    global user_position
    global user_filename
    global user_disclosure

    global c_user_email
    global c_user_phone
    global c_user_position
    global c_user_filename

    if c_user_email:
        user_email = update.message.text
        c_user_email = False

    if c_user_phone:
        user_phone = update.message.text
        c_user_phone = False

    if c_user_position:
        user_position = update.message.text
        c_user_position = False

    if c_user_filename:
        user_filename = update.message.document.file_name
        c_user_filename = False

    update.message.reply_text(
        '<b><u>Details Entered:</u></b>\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nPosition Applied: {position}\nFile Uploaded: {file}'
            .format(name=update.message.from_user.first_name, email=user_email, phone=user_phone,
                    position=user_position, file=user_filename),
        parse_mode=ParseMode.HTML)

    menu_keyboard = [
        ["Email", "Phone"],
        ["Resume", "Position"],
        ["No Changes"],
    ]

    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

    update.message.reply_text("Would you like to make any changes?", reply_markup=menu_markup)

    return CONFIRM


def ia_end(update: Update, context: CallbackContext) -> int:
    global user_email
    global user_phone
    global user_position
    global user_filename
    global user_update_file
    global user_disclosure
    global user_file

    global c_user_email
    global c_user_phone
    global c_user_position
    global c_user_filename

    def getCredentials():
        credentials = None
        SCOPES = 'https://www.googleapis.com/auth/drive'

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                credentials = pickle.load(token)
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                mac = '/credentials.json'
                win = '\\credentials.json'
                flow = InstalledAppFlow.from_client_secrets_file(
                    cwd + mac, SCOPES)
                credentials = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(credentials, token)

        return credentials

    user_file.download(user_filename)

    print("d1")

    doc = user_update_file

    service = build('drive', 'v3', credentials=getCredentials(), cache_discovery=False)
    filename = doc.file_name

    print("d2")

    metadata = {'name': filename}

    print("d2.1")
    media = MediaFileUpload(filename, chunksize=1024 * 1024, mimetype=doc.mime_type, resumable=True)

    print("d2.2")
    request = service.files().create(body=metadata,
                                     media_body=media)

    print("d3")

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print("Uploaded %d%%." % int(status.progress() * 100))

    print("d4")

    context.bot.send_message(chat_id=update.effective_chat.id, text="✅ File uploaded!")

    update.message.reply_text('Thank you! I hope we can talk again some day.')

    jobID = int(user_position.split(" ")[0][5:len(user_position.split(" ")[0]) - 1])

    db.addJobApplication(str(update.message.from_user.first_name), str(user_email), str(user_phone),
                         str(user_filename), jobID)

    user_email = None
    user_phone = None
    user_position = None
    user_filename = None
    user_update_file = None
    user_file = None
    user_disclosure = None

    c_user_email = False
    c_user_phone = False
    c_user_position = False
    c_user_filename = False

    return ConversationHandler.END


def ia_do_resubmit(update: Update, context: CallbackContext):
    global user_email
    global user_phone
    global user_position
    global user_filename
    global user_disclosure

    global c_user_email
    global c_user_phone
    global c_user_position
    global c_user_filename

    if str(update.message.text) == "Email":
        update.message.reply_text('Enter your email:')
        c_user_email = True
        return C_EMAIL

    elif str(update.message.text) == "Phone":
        update.message.reply_text('Enter your phone:')
        c_user_phone = True
        return C_PHONE

    elif str(update.message.text) == "Resume":
        update.message.reply_text('Enter your file:')
        c_user_filename = True
        return C_FILE

    elif str(update.message.text) == "Position":
        menu_keyboard = []
        for position in db.getAvailablePositions():
            menu_keyboard.append(["JobID{Id}: {Position}, {Type}"
                                 .format(Id=position[0], Position=position[1], Type=position[2])])
        menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
        update.message.reply_text('Enter your position:', reply_markup=menu_markup)
        c_user_position = True
        return C_POSITION

    else:
        update.message.reply_text(
            '<b><u>Details Entered:</u></b>\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nPosition Applied: {position}\nFile Uploaded: {file}'
                .format(name=update.message.from_user.first_name, email=user_email, phone=user_phone,
                        position=user_position, file=user_filename),
            parse_mode=ParseMode.HTML)

        menu_keyboard = [
            ["Email", "Phone"],
            ["Resume", "Position"],
            ["No Changes"],
        ]

        menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

        update.message.reply_text("Would you like to make any changes?", reply_markup=menu_markup)

        return CONFIRM


def ia_reject_submit(update: Update, context: CallbackContext):
    menu_keyboard = [
        ["Email", "Phone"],
        ["Resume", "Position"],
        ["No Changes"],
    ]
    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Wrong format! Click on one of the buttons please', reply_markup=menu_markup)


def cl_ask_id(update: Update, context: CallbackContext):
    update.message.reply_text('Hi! Please provide your company ID!')
    return ID


def cl_ask_amount(update: Update, context: CallbackContext):
    global cl_id
    cl_id = update.message.text
    update.message.reply_text('ID entered: <b>{id}</b>'.format(id=update.message.text),
                              parse_mode=ParseMode.HTML)
    update.message.reply_text('Hi! Please enter the amount to be reimbursed!')
    return AMOUNT


def cl_ask_receipt(update: Update, context: CallbackContext):
    global cl_amount
    cl_amount = update.message.text
    update.message.reply_text('Amount entered: <b>{amount}</b>'.format(amount=update.message.text),
                              parse_mode=ParseMode.HTML)
    update.message.reply_text('Hi! Please upload picture/document of receipt')
    return RECEIPT


def cl_ask_confirm(update: Update, context: CallbackContext):
    global cl_receipt_name
    global cl_update_receipt
    global cl_receipt

    cl_receipt_name = update.message.document.file_name

    cl_receipt = context.bot.getFile(update.message.document.file_id)

    cl_update_receipt = update.message.document

    update.message.reply_text('Receipt uploaded: <b><u>{filename}</u></b>'.format(filename=cl_receipt_name),
                              parse_mode=ParseMode.HTML)

    global cl_id
    global cl_amount

    global c_cl_id
    global c_cl_amount
    global c_cl_receipt_name

    if c_cl_id:
        cl_id = update.message.text
        c_cl_id = False

    if c_cl_amount:
        cl_amount = update.message.text
        c_cl_amount = False

    if c_cl_receipt_name:
        cl_receipt_name = update.message.document.file_name
        c_cl_receipt_name = False

    update.message.reply_text(
        '<b><u>Details Entered:</u></b>\n\nName: {name}\nID: {id}\nAmount: {amount}\nReceipt Uploaded: {file}'
            .format(name=update.message.from_user.first_name,
                    id=cl_id,
                    amount=cl_amount,
                    file=cl_receipt_name),
        parse_mode=ParseMode.HTML)

    menu_keyboard = [
        ["ID", "Amount", "Receipt"],
        ["No Changes"],
    ]

    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

    update.message.reply_text("Would you like to make any changes?", reply_markup=menu_markup)

    return CL_CONFIRM


def cl_ask_re_confirm(update: Update, context: CallbackContext):
    global cl_receipt_name
    global cl_update_receipt
    global cl_receipt

    global cl_id
    global cl_amount

    global c_cl_id
    global c_cl_amount
    global c_cl_receipt_name

    if c_cl_id:
        cl_id = update.message.text
        c_cl_id = False

    if c_cl_amount:
        cl_amount = update.message.text
        c_cl_amount = False

    if c_cl_receipt_name:
        cl_receipt_name = update.message.document.file_name
        c_cl_receipt_name = False

    update.message.reply_text(
        '<b><u>Details Entered:</u></b>\n\nName: {name}\nID: {id}\nAmount: {amount}\nReceipt Uploaded: {file}'
            .format(name=update.message.from_user.first_name,
                    id=cl_id,
                    amount=cl_amount,
                    file=cl_receipt_name),
        parse_mode=ParseMode.HTML)

    menu_keyboard = [
        ["ID", "Amount", "Receipt"],
        ["No Changes"],
    ]

    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

    update.message.reply_text("Would you like to make any changes?", reply_markup=menu_markup)

    return CL_CONFIRM


def cl_do_resubmit(update: Update, context: CallbackContext):
    global cl_id
    global cl_amount
    global cl_receipt
    global cl_update_receipt
    global cl_receipt_name

    global c_cl_id
    global c_cl_amount
    global c_cl_receipt_name

    if str(update.message.text) == "ID":
        update.message.reply_text('Enter your company ID:')
        c_cl_id = True
        return C_ID

    elif str(update.message.text) == "Amount":
        update.message.reply_text('Enter your amount:')
        c_cl_amount = True
        return C_AMOUNT

    elif str(update.message.text) == "Receipt":
        update.message.reply_text('Upload your receipt:')
        c_cl_receipt_name = True
        return C_RECEIPT

    else:

        update.message.reply_text(
            '<b><u>Details Entered:</u></b>\n\nName: {name}\nID: {id}\nAmount: {amount}\nReceipt Uploaded: {file}'
                .format(name=update.message.from_user.first_name,
                        id=cl_id,
                        amount=cl_amount,
                        file=cl_receipt_name),
            parse_mode=ParseMode.HTML)

        menu_keyboard = [
            ["ID", "Amount", "Receipt"],
            ["No Changes"],
        ]

        menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

        update.message.reply_text("Would you like to make any changes?", reply_markup=menu_markup)

        return CL_CONFIRM


def cl_end(update: Update, context: CallbackContext):

    global cl_id
    global cl_amount
    global cl_receipt
    global cl_update_receipt
    global cl_receipt_name

    global c_cl_id
    global c_cl_amount
    global c_cl_receipt_name

    def getCredentials():
        credentials = None
        SCOPES = 'https://www.googleapis.com/auth/drive'

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                credentials = pickle.load(token)
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                mac = '/credentials.json'
                win = '\\credentials.json'
                flow = InstalledAppFlow.from_client_secrets_file(
                    cwd + mac, SCOPES)
                credentials = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(credentials, token)

        return credentials

    cl_receipt.download(cl_receipt_name)

    doc = cl_update_receipt

    service = build('drive', 'v3', credentials=getCredentials(), cache_discovery=False)
    filename = doc.file_name

    metadata = {'name': filename}
    media = MediaFileUpload(filename, chunksize=1024 * 1024, mimetype=doc.mime_type, resumable=True)
    request = service.files().create(body=metadata,
                                     media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print("Uploaded %d%%." % int(status.progress() * 100))

    context.bot.send_message(chat_id=update.effective_chat.id, text="✅ File uploaded!")

    db.addClaim(company_id=cl_id, name=update.message.from_user.first_name,
                amount=cl_amount, filename=cl_receipt_name)

    update.message.reply_text('Thank you! I hope we can talk again some day.')

    cl_id = None
    cl_amount = None
    cl_receipt = None
    cl_update_receipt = None
    cl_receipt_name = None

    c_cl_id = False
    c_cl_amount = False
    c_cl_receipt_name = False

    return ConversationHandler.END


def em_show_faqs(update: Update, context: CallbackContext):

    base = "<b><u>Frequently Asked Questions:</u></b>\n\n"

    for row in db.getQuestionsAndAnswers():
        base += ("<b>" + str(row[0]) + "</b>\n")
        if row[1] is None or row[1] is "":
            base += "\n"
        else:
            base += (str(row[1]) + "\n")
        base += "\n"

    menu_keyboard = [
        ["Done", "Ask another question!"],
    ]

    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

    update.message.reply_text(base, parse_mode=ParseMode.HTML, reply_markup=menu_markup)

    return NAVIGATION


def em_add_question(update: Update, context: CallbackContext) -> int:
    if str(update.message.text) == "Done":
        update.message.reply_text('Thank you! I hope we can talk again some day.')
        return ConversationHandler.END
    elif str(update.message.text) == "Ask another question!":
        update.message.reply_text('What is your question?')
        return ADD
    else:
        base = "<b><u>Frequently Asked Questions:</u></b>\n\n"
        for row in db.getQuestionsAndAnswers():
            base += ("<b>" + str(row[0]) + "</b>\n")
            if row[1] is None or row[1] is "":
                base += "\n"
            else:
                base += (str(row[1]) + "\n")
            base += "\n"
        menu_keyboard = [
            ["Done", "Ask another question!"],
        ]
        menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
        update.message.reply_text(base, parse_mode=ParseMode.HTML, reply_markup=menu_markup)
        return NAVIGATION


def em_confirm_add(update: Update, context: CallbackContext) -> int:
    global em_add
    global c_em_add
    em_add = update.message.text
    menu_keyboard = [
        ["Edit", " Submit"],
    ]
    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Entered question: <b>{question}</b>'.format(question=update.message.text),
                              parse_mode=ParseMode.HTML)
    update.message.reply_text("Press 'Submit' to confirm and submit question", reply_markup=menu_markup)

    return C_ADD


def em_submit_question(update: Update, context: CallbackContext) -> int:
    if update.message.text == "Submit":
        global em_add
        global c_em_add
        db.addQuestion(update.message.from_user.first_name, em_add)
        update.message.reply_text('Question asked! We will get back to you soon!')
        base = "<b><u>Frequently Asked Questions:</u></b>\n\n"

        for row in db.getQuestionsAndAnswers():
            base += ("<b>" + str(row[0]) + "</b>\n")
            if row[1] is None or row[1] is "":
                base += "\n"
            else:
                base += (str(row[1]) + "\n")
            base += "\n"

        menu_keyboard = [
            ["Done", "Ask another question!"],
        ]

        menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

        update.message.reply_text(base, parse_mode=ParseMode.HTML, reply_markup=menu_markup)
        return NAVIGATION

    elif update.message.text == "Edit":
        update.message.reply_text("Re-enter question to ask:")
        return ADD

    else:
        menu_keyboard = [
            ["Edit", " Submit"],
        ]
        menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
        update.message.reply_text('Entered question: <b>{question}</b>'.format(question=update.message.text),
                                  parse_mode=ParseMode.HTML)
        update.message.reply_text("Press 'Submit' to confirm and submit question", reply_markup=menu_markup)
        return C_ADD


def vt_start_tour(update: Update, context: CallbackContext) -> int:
    menu_keyboard = [
        ["Mission", " Vision"],
        ["Key Personnel", "Office Layout"],
        ["New hires checklist", "Done"]
    ]
    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

    if update.message.text == "Mission" or update.message.text == "Vision" or update.message.text == "Key Personnel" \
            or update.message.text == "Office Layout" or update.message.text == "Done" \
            or update.message.text == "New hires checklist":
        if update.message.text == "Done":
            update.message.reply_text('Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        elif update.message.text == "Mission":
            # Mission Statement
            mission_statement = "The mission of this company is to..."
            update.message.reply_text(mission_statement, parse_mode=ParseMode.HTML, reply_markup=menu_markup)
            return CONTROL
        elif update.message.text == "Vision":
            # Vision Statement
            vision_statement = "The vision of this company is to..."
            update.message.reply_text(vision_statement, parse_mode=ParseMode.HTML, reply_markup=menu_markup)
            return CONTROL
        elif update.message.text == "Key Personnel":
            # Key Personnel Statement
            menu_inline_keyboard = [
                [InlineKeyboardButton("CEO", callback_data='ceo'), InlineKeyboardButton("CTO", callback_data='cto')],
                [InlineKeyboardButton("CFO", callback_data='cfo'), InlineKeyboardButton("HR Manager", callback_data='hr')],
                [InlineKeyboardButton("Done", callback_data='del')]
            ]
            menu_inline_keyboard_reply = InlineKeyboardMarkup(menu_inline_keyboard)
            update.message.reply_text('Click on any one of the buttons to reveal more information about them!', parse_mode=ParseMode.HTML, reply_markup=menu_inline_keyboard_reply)
            return CONTROL
        elif update.message.text == "New hires checklist":
            update.message.reply_document(caption='Great! Now that you are one of us, I need some paperwork done and documents submitted: \n\n\n1. For administrating your salary, submit your bank details\n\n2. To generate your access card, send me your NRIC and work ID\n\n3. Read the memo attached to you on working etiquette',
                                          document=open("assets/memo.txt", 'rb'), parse_mode=ParseMode.HTML, reply_markup=menu_markup)
            return CONTROL
        else:
            # Layout
            update.message.reply_photo(photo=open("assets/layout.png", 'rb'), caption='Office Layout:\n\n1. Working Desks 1\n2. Pantry\n3. Toilets, Storeroom, Server Room\n4. Conference Rooms \n5. Working Desks 2\n6. Chill Rooms 1\n7. Executive Desks\n8. Chill Rooms 2', parse_mode=ParseMode.HTML, reply_markup=menu_markup)
            return CONTROL

    else:
        update.message.reply_document(
            caption="Hi {name}! Welcome to John Doe's HR Consultancy! Glad to have you here!\n\n <INSERT MORE DETAILS HERE>".format(
            name=update.message.from_user.first_name),
            document="https://media4.giphy.com/media/y8Mz1yj13s3kI/giphy.gif"
        )
        update.message.reply_text(
            "That's all I have to share for now! Click any one of the following buttons to find out more!",
            reply_markup=menu_markup)

        return CONTROL


def button(update: Update, context: CallbackContext) -> None:
    menu_keyboard = [
        ["Mission", " Vision"],
        ["Key Personnel", "Office Layout"],
        ["New hires checklist", "Done"]
    ]
    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
    query = update.callback_query
    query.answer()
    if query.data == 'ceo':
        context.bot.send_photo(photo=open("assets/ceo.jpeg", 'rb'), caption="This is Tom our CEO!", chat_id=update.callback_query.message.chat.id)

    if query.data == 'cfo':
        context.bot.send_photo(photo=open("assets/cfo.jpeg", 'rb'), caption="This is Jerry our CEO!", chat_id=update.callback_query.message.chat.id)

    if query.data == 'cto':
        context.bot.send_photo(photo=open("assets/cto.jpeg", 'rb'), caption="This is Spike our CTO!", chat_id=update.callback_query.message.chat.id)

    if query.data == 'hr':
        context.bot.send_photo(photo=open("assets/hr.jpeg", 'rb'), caption="This is Butch our HR Manager!", chat_id=update.callback_query.message.chat.id)

    if query.data == 'del':
        query.delete_message()
        context.bot.send_message(text="Alright, now that you have a better idea of our key appointment holders, lets carry on with the onboarding process :)", reply_markup=menu_markup, chat_id=update.callback_query.message.chat.id)



def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    ia_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Job Application'), ia_ask_email)],
        states={
            EMAIL: [MessageHandler(Filters.entity('email'), ia_ask_phone),
                    MessageHandler(~Filters.entity('email'), ia_reject_email)],
            PHONE: [MessageHandler(Filters.regex('^[0-9]*$'), ia_ask_position),
                    MessageHandler(~Filters.regex('^[0-9]*$'), ia_reject_phone)],
            POSITION: [MessageHandler(Filters.text, ia_ask_file)],
            FILE: [MessageHandler(telegram.ext.filters.MergedFilter(base_filter=Filters.document.pdf,
                                                                    or_filter=Filters.document.docx),
                                  ia_ask_disclosure),
                   MessageHandler(~telegram.ext.filters.MergedFilter(base_filter=Filters.document.pdf,
                                                                     or_filter=Filters.document.docx),
                                  ia_reject_file)],
            DISCLOSURES: [MessageHandler(Filters.regex('^(Yes)$'), ia_ask_confirm),
                          MessageHandler(~Filters.regex('^(Yes)$'), ia_reject_disclosures)],
            CONFIRM: [MessageHandler(Filters.regex('No Changes'), ia_end),
                      MessageHandler(~Filters.regex('No Changes'), ia_do_resubmit)],

            C_EMAIL: [MessageHandler(Filters.entity('email'), ia_ask_confirm),
                      MessageHandler(~Filters.entity('email'), ia_reject_email)],

            C_PHONE: [MessageHandler(Filters.regex('^[0-9]*$'), ia_ask_confirm),
                      MessageHandler(~Filters.regex('^[0-9]*$'), ia_reject_phone)],

            C_POSITION: [MessageHandler(Filters.text, ia_ask_confirm)],

            C_FILE: [MessageHandler(telegram.ext.filters.MergedFilter(base_filter=Filters.document.pdf,
                                                                      or_filter=Filters.document.docx),
                                    ia_ask_confirm),
                     MessageHandler(~telegram.ext.filters.MergedFilter(base_filter=Filters.document.pdf,
                                                                       or_filter=Filters.document.docx),
                                    ia_reject_file)],
        },
        fallbacks=[MessageHandler(Filters.command, cancel)],
        allow_reentry=True
    )

    vt_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Digital Onboarding'), vt_start_tour)],
        states={
            CONTROL: [MessageHandler(Filters.text, vt_start_tour)],
        },
        fallbacks=[MessageHandler(Filters.command, cancel)],
        allow_reentry=True
    )

    em_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Employee FAQs'), em_show_faqs)],
        states={
            NAVIGATION: [MessageHandler(Filters.text, em_add_question)],
            ADD: [MessageHandler(Filters.text, em_confirm_add)],
            C_ADD: [MessageHandler(Filters.regex('Submit'), em_submit_question),
                    MessageHandler(Filters.regex('Edit'), em_submit_question),
                    MessageHandler(~telegram.ext.filters.MergedFilter(base_filter=Filters.regex('Submit'),
                                                                      or_filter=Filters.regex('Edit')),
                                   em_submit_question),
                    ]
        },
        fallbacks=[MessageHandler(Filters.command, cancel)],
        allow_reentry=True
    )

    cl_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Submit Claims'), cl_ask_id)],
        states={
            ID: [MessageHandler(Filters.text, cl_ask_amount)],
            AMOUNT: [MessageHandler(Filters.regex('^[0-9]*.?[0-9]*$'), cl_ask_receipt)],
            RECEIPT: [MessageHandler(Filters.document.image, cl_ask_confirm),
                      MessageHandler(Filters.document.pdf, cl_ask_confirm),
                      MessageHandler(Filters.document.docx, cl_ask_confirm),
                      MessageHandler(Filters.document.doc, cl_ask_confirm)],
            C_ID: [MessageHandler(Filters.text, cl_ask_re_confirm)],
            C_AMOUNT: [MessageHandler(Filters.regex('^[0-9]*.?[0-9]*$'), cl_ask_re_confirm)],
            C_RECEIPT: [MessageHandler(Filters.document.image, cl_ask_re_confirm),
                        MessageHandler(Filters.document.pdf, cl_ask_re_confirm),
                        MessageHandler(Filters.document.docx, cl_ask_re_confirm),
                        MessageHandler(Filters.document.doc, cl_ask_re_confirm)],
            CL_CONFIRM: [MessageHandler(Filters.regex('No Changes'), cl_end),
                         MessageHandler(~Filters.regex('No Changes'), cl_do_resubmit)]
        },
        fallbacks=[MessageHandler(Filters.command, cancel)],
        allow_reentry=True
    )

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(ia_handler)
    dp.add_handler(cl_handler)
    dp.add_handler(em_handler)
    dp.add_handler(vt_handler)

    dp.add_handler(CallbackQueryHandler(button))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    db.loadDB()
    db.loadQuery()

    main()
