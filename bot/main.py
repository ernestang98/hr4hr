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

from excel import getsheet, getcol, checktimeavailfordate, makebooking

import telegramcalendar, telegramjcalendar
import utils
import messages

cwd = os.path.dirname(os.path.abspath(__file__))
os.chdir(cwd)

TOKEN = "2031856383:AAFF6o2soJqqbZMxeRx9UFFcB0irtKjynfE"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL, PHONE, POSITION, FILE, DISCLOSURES, CONFIRM, SECOND_EMAIL, C_EMAIL, C_PHONE, C_POSITION, C_FILE = range(11)

PERSON, ID, AMOUNT, RECEIPT, C_ID, C_AMOUNT, C_RECEIPT, CL_CONFIRM, PERSON_RE = range(11, 20)

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

the_sheet_customer = None
the_sheet_boss = None
cl_person = None
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
        ["Our Services"],
        ["Meet the Team"],
        ["Book Appointment"],
        ["FAQs"],
        ["Exit! Thank you!"]
    ]

    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

    update.message.reply_text('Good ' + greeting + str(get_member) + "!"
                              + '\nWhat would you like to do today?', reply_markup=menu_markup)


def ia_ask_email(update: Update, context: CallbackContext) -> int:
    update.message.reply_photo(photo=open("assets/picture.jpg", 'rb'), caption='These are the services we offer!\n\nIf you are unsure on which products/services suits you, try our quiz at https://www.aveda.com/hair-quiz/find-best-haircare-products?_step=hair_type', parse_mode=ParseMode.HTML)
    return ConversationHandler.END


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
        "<b>PRIVACY STATEMENT</b>\n We reserve the right to make changes to this Privacy Policy at any time and for any reason. We will alert you about any changes by updating the “Last Updated” date of this Privacy Policy. Any changes or modifications will be effective immediately upon posting the updated Privacy Policy on the Site, and you waive the right to receive specific notice of each such change or modification. You are encouraged to periodically review this Privacy Policy to stay informed of updates. You will be deemed to be aware of, will be subject to, and will be deemed to have accepted the changes in any revised Privacy Policy by your continued use of the Site after the date such revised Privacy Policy is posted.\n\n\n\n\n\nPlease press <b>Yes</b> to provide your permission and to recognise that you have read this entire policy",
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


def cl_ask_person(update: Update, context: CallbackContext):
    update.message.reply_document(caption='Attached is the booking list for each hairdresser!', document=open("excel-customer.xlsx", 'rb'))
    menu_keyboard = [
        ["Bowie Chan", "John Boo"],
        ["Lawrence", "Claudia Tong"],
        ["Jess Zhang", "No Preference"]
    ]
    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Pick your preferred Hairdresser!', reply_markup=menu_markup)
    return PERSON


def cl_ask_id(update: Update, context: CallbackContext):

    global cl_person

    cl_person = update.message.text

    update.message.reply_text(text=messages.calendar_message,
                    reply_markup=telegramcalendar.create_calendar())
    return ID


def inline_handler(update, context):
    try:
        query = update.callback_query
        (kind, _, _, _, _) = utils.separate_callback_data(query.data)
        if kind == messages.CALENDAR_CALLBACK:
            inline_calendar_handler(update, context)
        elif kind == messages.JCALENDAR_CALLBACK:
            inline_jcalendar_handler(update, context)                                   
    except:
        button(update, context)


def inline_calendar_handler(update, context):
    selected,date = telegramcalendar.process_calendar_selection(update, context)
    if selected:
        context.bot.send_message(chat_id=update.callback_query.from_user.id,
                        text=messages.calendar_response_message % (date.strftime("%d/%m/%Y")),
                        reply_markup=ReplyKeyboardRemove())
        global cl_id
        cl_id = date.strftime("%d/%m/%Y")
        menu_keyboard = [
            ["Confirm", "Rechoose"],
        ]
        menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
        context.bot.send_message(chat_id=update.callback_query.from_user.id, text='Type <b>Confirm</b> to proceed or <b>Rechoose</b> to reselect date (case sensitive)', parse_mode=ParseMode.HTML, reply_markup=menu_markup)

def inline_jcalendar_handler(update: Update, context: CallbackContext):
    selected, date = telegramjcalendar.process_calendar_selection(context.bot, update)
    if selected:
        context.bot.send_message(chat_id=update.callback_query.from_user.id,
                text=messages.jcalendar_response_message % date,
                reply_markup=ReplyKeyboardRemove())


def cl_ask_amount(update: Update, context: CallbackContext):
    global cl_id
    global cl_person
    global the_sheet_customer
    global the_sheet_boss

    text = update.message.text

    if text == "Confirm":

        if getsheet(str(cl_person)) != None:
            the_sheet_customer, the_sheet_boss = getsheet(str(cl_person))
            print(cl_id)
            empty_slots = checktimeavailfordate(str(cl_id), the_sheet_customer)
            if empty_slots == [] or empty_slots is None or empty_slots == "Error":
                menu_keyboard = [
                    ["Bowie Chan", "John Boo"],
                    ["Lawrence", "Claudia Tong"],
                    ["Jess Zhang", "No Preference"]
                ]
                update.message.reply_text("No more slot, pick again!")
                menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
                update.message.reply_text('Pick your preferred Hairdresser!', reply_markup=menu_markup)
                return PERSON
            else:
                menu_keyboard = []
                if 0 < len(empty_slots) and len(empty_slots) <= 4:
                    first_layer = []
                    for i in range(len(empty_slots)):
                        first_layer.append(empty_slots[i])
                    menu_keyboard.append(first_layer)
                elif 4 < len(empty_slots) and len(empty_slots) <= 8:
                    first_layer = []
                    second_layer = []
                    for i in range(4):
                        first_layer.append(empty_slots[i])
                    for i in range(4, len(empty_slots)):
                        second_layer.append(empty_slots[i])
                    menu_keyboard.append(first_layer)
                    menu_keyboard.append(second_layer)
                else:    
                    first_layer = []
                    second_layer = []
                    third_layer = []
                    for i in range(4):
                        first_layer.append(empty_slots[i])
                    for i in range(4, 8):
                        second_layer.append(empty_slots[i])
                    for i in range(8, len(empty_slots)):
                        third_layer.append(empty_slots[i])
                    menu_keyboard.append(first_layer)
                    menu_keyboard.append(second_layer)
                    menu_keyboard.append(third_layer)
        else:
            menu_keyboard = [
                ["0900", "1000", "1100", "1200"],
                ["1300", "1400", "1500", "1600"],
                ["1700", "1800"],
            ]

        menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
        update.message.reply_text("Pick a time:", reply_markup=menu_markup)

        return AMOUNT

    else:
        update.message.reply_text(text=messages.calendar_message,
                        reply_markup=telegramcalendar.create_calendar())
        return ID


def cl_ask_receipt(update: Update, context: CallbackContext):
    global cl_amount
    cl_amount = update.message.text
    print(cl_amount)
    update.message.reply_text("Please enter the following details:\n1. Name\n2. Email\n3. Contact Number\n4. Service\n5. Hairdresser (Optional)\n6. Any additional comments")
    return RECEIPT


def cl_ask_location(update: Update, context: CallbackContext):
    global cl_receipt
    cl_receipt = update.message.text
    menu_keyboard = [
        ["Reselect", "Done"],
    ]
    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text("Date selected:\n{cl_id}\n\nTime selected:\n{cl_amount}\n\nDetails entered:\n{cl_receipt}".format(cl_id=cl_id, cl_amount=cl_amount, cl_receipt=cl_receipt))
    update.message.reply_text("Confirm your details:", reply_markup=menu_markup)

    return C_ID


def cl_ask_confirm(update: Update, context: CallbackContext):
    text = update.message.text

    if text == "Reselect":
        update.message.reply_document(caption='Attached is the booking list for each hairdresser!', document=open("excel-customer.xlsx", 'rb'))
        menu_keyboard = [
            ["Bowie Chan", "John Boo"],
            ["Lawrence", "Claudia Tong"],
            ["Jess Zhang", "No Preference"]
        ]
        menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
        update.message.reply_text('Pick your preferred Hairdresser!', reply_markup=menu_markup)
        return PERSON
    else:
        global cl_receipt
        update.message.reply_text("Thank you for booking! Our staff will contact you shortly to confirm your slot (subject to availability).")
        makebooking(cl_amount, cl_id, the_sheet_customer, the_sheet_boss, cl_receipt)
        return ConversationHandler.END


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
        if row[1] is None or row[1] == "":
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
            if row[1] is None or row[1] == "":
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
            if row[1] is None or row[1] == "":
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

    if update.message.text == "Mission" or update.message.text == "Vision" or update.message.text == "Key Personnel" \
            or update.message.text == "Office Layout" or update.message.text == "Done" \
            or update.message.text == "New hires checklist":
        if update.message.text == "Done":
            update.message.reply_text('Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END

    menu_inline_keyboard = [
                [InlineKeyboardButton("Bowie Chan", callback_data='ceo'), InlineKeyboardButton("John Boo", callback_data='cto')],
                [InlineKeyboardButton("Lawrence", callback_data='cfo'), InlineKeyboardButton("Claudia Tong", callback_data='hr')],
                [InlineKeyboardButton("Jess Zhang", callback_data='jz'), InlineKeyboardButton("Done", callback_data='del')]
            ]
    menu_inline_keyboard_reply = InlineKeyboardMarkup(menu_inline_keyboard)
    update.message.reply_text('Click on any one of the buttons to reveal more information about them!', parse_mode=ParseMode.HTML, reply_markup=menu_inline_keyboard_reply)
    return CONTROL


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if query.data == 'ceo':
        context.bot.send_photo(photo=open("assets/bowie.jpg", 'rb'), caption="Name: Bowie Chan\n\nIntroduction: Hi I am Bowie! I love to do hair highlights for my customers! Are you someone who wants to freshen up your tresses without having to commit to full colour? Hair highlights may well be the answer you’ve been searching for. We have a variety of options from blonde to brown here at TS! Don't worry if it is your first time, come look for me and we will figure something out just for you!\n\nExperience: 2 years\n\nSpeciality: Highlights, perm, styling\n\nInstagram: @bowiechan___", chat_id=update.callback_query.message.chat.id)

    if query.data == 'cto':
        context.bot.send_photo(photo=open("assets/john.jpg", 'rb'), caption="Name: John Boo\n\nIntroduction: Hi I am John! I enjoy trying out the different hair styles on my customers. Let me know what hair trend you are interested in and I will do the job for you! Many of my customers call me the funny guy because I enjoy cracking a dad joke or two during the hair styling sessions! If you are looking to try out different hair cuts or styling methods, hit me up at TS!\n\nExperience: 3 years\n\nSpeciality: Styling, haircut design\n\nInstagram: @hairbyjohnboo", chat_id=update.callback_query.message.chat.id)

    if query.data == 'cfo':
        context.bot.send_photo(photo=open("assets/lawrence.jpg", 'rb'), caption="Name: Lawrence\n\nIntroduction: Do you like bold hair colours? Or are you just very bored of your current hair? You have come to the right person! I am Lawrence and when it comes to hair colours, I really believe, the bolder the better. ;) I love keeping up to date with the current hair trends, so if you are looking for someone to do a wave perm, digital perm or any other perm for you, look for me anytime! I am so ready to style your hair!\nExperience: 1 year\n\nSpeciality: Perm, hair dye, treatment\n\nInstagram: @hairby.lawrence", chat_id=update.callback_query.message.chat.id)

    if query.data == 'jz':
        context.bot.send_photo(photo=open("assets/jess.jpg", 'rb'), caption="Name: Jess Zhang\n\nIntroduction: Hello I am Jess! I love cooking, playing sports and also having a good chat with my customers! Don't worry about being bored at your hair sessions, I am always up for a conversation! If you are worried about damaged hair due to constant hair dyeing or bleaching, fret not. Organic products are used at TS as we just want the best for our customers!\n\nExperience: 4 years\n\nSpeciality: Creative, Hair dye, bleaching\n\nInstagram: @zhang.jess", chat_id=update.callback_query.message.chat.id)

    if query.data == 'hr':
        context.bot.send_photo(photo=open("assets/claudia.jpg", 'rb'), caption="Name: Claudia Tong\n\nIntroduction: Are you riding on the Korean wave? Thinking of getting air bangs, curtain bangs or even the Korean perm? Simply look for me at Team Salon! I am Claudia and I love being creative with the different hair designs. What matters to me most is seeing the satisfied smiles on my customers' faces at the end of every hair session. Don't wait any longer, come get your hair done at TS! I look forward to meeting you :)\n\nExperience: 6 years\n\nSpeciality: Creative, Styling, korean perm\n\nInstagram: @claudia_hairart", chat_id=update.callback_query.message.chat.id)

    if query.data == 'del':
        query.delete_message()
        context.bot.send_message(text="Thank you!", chat_id=update.callback_query.message.chat.id)



def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    ia_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Our Services'), ia_ask_email)],
        states={
            EMAIL: [MessageHandler(Filters.text, ia_ask_confirm)],
        },
        fallbacks=[MessageHandler(Filters.command, cancel)],
        allow_reentry=True
    )

    vt_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Meet the Team'), vt_start_tour)],
        states={
            CONTROL: [MessageHandler(Filters.text, vt_start_tour)],
        },
        fallbacks=[MessageHandler(Filters.command, cancel)],
        allow_reentry=True
    )

    em_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('FAQs'), em_show_faqs)],
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
        entry_points=[MessageHandler(Filters.regex('Book Appointment'), cl_ask_person)],
        states={
            PERSON: [MessageHandler(Filters.text, cl_ask_id)],
            ID: [MessageHandler(telegram.ext.filters.MergedFilter(base_filter=Filters.regex('Confirm'),
                                                                      or_filter=Filters.regex('Rechoose')), cl_ask_amount)],
            AMOUNT: [MessageHandler(Filters.regex('^[0-9]*.?[0-9]*$'), cl_ask_receipt)],
            RECEIPT: [MessageHandler(Filters.text, cl_ask_location)],
            C_ID: [MessageHandler(Filters.text, cl_ask_confirm)],
            PERSON_RE: [MessageHandler(Filters.text, cl_ask_person)]
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
    dp.add_handler(CallbackQueryHandler(inline_handler))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
