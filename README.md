## Project Summary

Telegram Bot using Python which assists HR departments by allowing end-users to perform the following tasks: Claims submission, Job/Internship applications, onboarding new employees and interns, as well as handling FAQs while allowing end-users to submit new questions. For the database, Google Drive API was used to store files uploaded while SQLite3 was used to store textual based data obtained or used by the above mentioned tasks.

### Telegram Bot (`bot/` directory)

- `main branch` (above-mentioned functionalities)

- `v2 branch` (slightly different functionalities) 

  - FAQs
  
  - appointment booking functionality
  
  - meet the team
  
  - list of service provided

- Add credentials.json file for [google drive](https://developers.google.com/drive/api/v3/about-auth)

- Add Bot token from bot father

### Flask Web App (`web/` directory)

- Used to administrate details provided by the bot (handle requests, configure onboarding process etc.)

- Incomplete/Work in progress (had no time to finish)

### Set up (Root Directory)

- Create venv

- Activate venv

- pip3 install -r requirements.txt

- For Web App: `cd web && flask run`

- For Bot: `cd bot && python3 main.py`
