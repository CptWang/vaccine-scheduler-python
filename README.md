# Python Application for Vaccine Scheduler

## Installation

1. Clone this repository
2. `pip install -r requirements.txt`

## Usage

### Setting up environment variables to access the database

Make sure to set this in the correct environment if you’re using virtual environments!

#### For Mac users:

Type in the commands in your terminal:

```bash
export Server=hw6vaccines.database.windows.net
export DBName=hw6
export UserID=wang
export Password=Wr!123456
```

Do note that those environment variables are only added for the current session. If you’d like to add those environment variables permanently, copy the exports and paste them into `.bash_profile` if you are using bash or `.zprofile` if you are using zsh.

#### For Windows users:

Open a command prompt and type:

```
setx Server "hw6vaccines.database.windows.net"
setx DBName "hw6"
setx UserID "wang"
setx Password "Wr!123456"
```

These environment variables will be saved permanently, and a “SUCCESS: Specified value was saved.” should be returned for each variable saved. To see these changes, close the command prompt and open a new command prompt, and type: `set`. This will return a list of your environment variables, and you should be able to see your new variables within this list.

### Using the scheduler system

Run `python src/main/scheduler/Scheduler.py` in the repository root directory. Follow the instructions prompted in the terminal and type in reasonable tokens, separated by single space. Typically, you should first create the caregiver and patient profile to advance.

## Future work

- Allow more robust mechanism to ensure atomicity.
- Rewrite cancel function for less redundancy.
- Implement more OOP (e.g. introduce an `Appointment` class) for better code structure and design.
- Etc.

## Acknowledgements

CSE414 Autumn 2021 HW6

Much thanks to Aaditya Desai and Aaditya Srivathsan for creating the starter code and [the original repo](https://github.com/aaditya1004/vaccine-scheduler-python) 

Much thanks to the instructor Ryan Maas and TA Alexander Hughes for in-person instructions about this HW.

Much thanks to other TA and students in CSE414 for providing meaningful and instructional discussions on Ed.
