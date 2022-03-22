# Parser for yarcheplus

This project is parser for site https://yarcheplus.ru/ (2022). 

## Getting Started
Python version: 3.9.10

Chrome version: 98.0.4758.80

Clone project:
```
git clone https://github.com/pymaster13/parser_yarche.git && cd parser_yarche
```

Create and activate virtual environment:
```
python3 -m venv venv && source venv/bin/activate
```

Install libraries:
```
python3 -m pip install -r requirements.txt
```

Run parser for getting categories:
```
python3 get_categories.py
```

Run parser for getting information about products:
```
python3 run.py
```

Functional:
- Authorization by phone number.
Step 1 - Enter your phone number. Simulate sending a 4-digit authorization code (delay
on the server 1-2 seconds).
Step 2 - to enter the code. If the user has not previously authorized, then record it in the database.
- Request for a user profile.
- The user needs to be assigned a randomly generated 6-digit invite code (numbers and symbols) at the first authorization.
- In the profile, the user should be able to enter someone else's invite code (when entering, check for existence). In your profile, you can activate only 1 invite code, if the user has already activated the invite code, then you need to display it in the appropriate field in the request for the user profile.
- The profile API should display a list of users (phone numbers) who entered the invite code of the current user.

Pythonanywhere: http://pymaster13.pythonanywhere.com/ (user database is SQLite because PGSQL is only allowed in paid account).
