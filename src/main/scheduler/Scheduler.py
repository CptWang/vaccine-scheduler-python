"""This module executes the vaccine scheduler system."""
from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import random

'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    """This function create a patient and store the username and password into the database."""
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    try:
        patient = Patient(username, salt=salt, hash=hash)
        # save to patient information to our database
        try:
            patient.save_to_db()
        except:
            print("Create failed, Cannot save")
            return
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create failed")
        return


def username_exists_patient(username):
    """This function checks if there is an existed username of the patient."""
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        # returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
        return
    cm.close_connection()
    return False


def create_caregiver(tokens):
    """This function create a caregiver and store the username and password into the database."""
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    try:
        caregiver = Caregiver(username, salt=salt, hash=hash)
        # save caregiver information to the database
        try:
            caregiver.save_to_db()
        except:
            print("Create failed, Cannot save")
            return
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create failed")
        return


def username_exists_caregiver(username):
    """This function checks if there is an existed username of the caregiver."""
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        # returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
        return
    cm.close_connection()
    return False


def login_patient(tokens):
    """This function logs in the patient with given username and password."""
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("Already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    # login
    try:
        try:
            patient = Patient(username, password=password).get()
        except:
            print("Get Failed")
            return
    except pymssql.Error:
        print("Error occurred when logging in")
        return

    # check if the login was successful
    if patient is None:
        print("Please try again!")
    else:
        print("Patient logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    """This function logs in the caregiver with given username and password."""
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("Already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    # login
    try:
        try:
            caregiver = Caregiver(username, password=password).get()
        except:
            print("Get Failed")
            return
    except pymssql.Error:
        print("Error occurred when logging in")
        return

    # check if the login was successful
    if caregiver is None:
        print("Please try again!")
    else:
        print("Caregiver logged in as: " + username)
        current_caregiver = caregiver


def get_schedule(d):
    """
    This internal method gets the available caregivers on the given date.
    --------
    Parameters:
    d: datetime in datetime(year, month, day) format
    --------
    Returns:
    caregiver_name: a list containing all usernames of available caregivers
    """
    # can also be written inside function search_caregiver_schedule(tokens)
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    caregiver_name = []

    get_caregiver_schedule = "SELECT Username FROM Availabilities WHERE Time = %s"
    try:
        cursor.execute(get_caregiver_schedule, d)
        for row in cursor:
            caregiver_name.append(row["Username"])
        return caregiver_name
    except pymssql.Error:
        print("Error occurred when getting caregivers' schedule")
        cm.close_connection()
        return


def get_vaccine():
    """
    This internal method gets all the vaccines' names with corresponding available doses.
    --------
    Returns:
    vaccines: a dictionary with all the vaccine names as keys, and their corresponding available doses as values
    """
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    vaccines = {}

    get_vaccines = "SELECT Name, Doses FROM Vaccines"
    try:
        cursor.execute(get_vaccines)
        for row in cursor:
            vaccines[row["Name"]] = row["Doses"]
        return vaccines
    except pymssql.Error:
        print("Error occurred when getting vaccines")
        cm.close_connection()
        return


def search_caregiver_schedule(tokens):
    """This function gets the available caregivers' names on the given date."""
    global current_caregiver
    global current_patient
    # check 1: if no one's already logged-in
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    # check 3: if the datetime format is correct
    date = tokens[1]
    fmt = "%m-%d-%Y"
    try:
        datetime.datetime.strptime(date, fmt)
    except ValueError:
        print("Wrong date format! Should be MM-DD-YYYY")
        return

    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

    # search available caregivers and vaccines
    try:
        try:
            available_caregiver = get_schedule(d)
            if len(available_caregiver) == 0:
                print("No caregiver is available on that day!")
                return
            vaccines = get_vaccine()
            print(available_caregiver)
            print(vaccines)
        except:
            print("Search Caregivers' Schedule Failed")
            return
    except pymssql.Error as db_err:
        print("Error occurred when searching caregivers' schedule")
        return


def appointment_id_exists(id):
    """
    This internal method checks if the randomly generated appointment ID is already in the database.
    --------
    Parameters:
    id: int
    --------
    Returns:
    True, if id equals to any appointment ID record in the database
    False, if id does not equal to any appointment ID record in the database
    """
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_id = "SELECT * FROM Appointments WHERE Id = %d"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_id, id)
        if cursor.rowcount != 0:
            return True
    except pymssql.Error:
        print("Error occurred when checking appointment ID")
        cm.close_connection()
        return
    cm.close_connection()
    return False


def delete_availability(date, name):
    """
    This internal method delete the given caregiver's availability on the given date from the database.
    --------
    Parameters:
    date: datetime in datetime(year, month, day) format
    name: str
    """
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    del_availability = "DELETE FROM Availabilities WHERE (Time = %s AND Username = %s)"
    try:
        cursor.execute(del_availability, (date, name))
        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error:
        print("Error occurred when delete availability")
        cm.close_connection()
        return
    cm.close_connection()


def add_availability(date, name):
    """
    This internal method add the given caregiver's availability on the given date into the database.
    --------
    Parameters:
    date: datetime in datetime(year, month, day) format
    name: str
    """
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    add_availability = "INSERT INTO Availabilities VALUES (%s , %s)"
    try:
        cursor.execute(add_availability, (date, name))
        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error:
        print("Error occurred when updating caregiver availability")
        cm.close_connection()
    cm.close_connection()


def check_appointment_date(pname, date):
    """
    This internal method check the given patient's appointment on the given date.
    --------
    Parameters:
    pname: str
    date: datetime in datetime(year, month, day) format
    --------
    Returns:
    True, if there exists an appointment for that patient
    False, if there does not exist an appointment for that patient
    """
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        check_date = "SELECT Time FROM Appointments WHERE Pusername = %s"
        cursor.execute(check_date, pname)
        for row in cursor:
            day = row["Time"]
            d = datetime.datetime.strftime(day, "%m-%d-%Y")
            if str(d) == date:
                print(f"You have already scheduled an appointment on {date}")
                return True
    except:
        print("Check appointment date failed")
        return True
    return False


def reserve(tokens):
    """This function reserve an appointment for a patient for the given vaccine name and date."""
    # check 1: check if the current logged-in user is a patient
    global current_patient
    if current_patient is None:
        print("Please login as a patient first!")
        return
    pname = current_patient.username

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    # check 3: if the datetime format is correct
    date = tokens[1]
    fmt = "%m-%d-%Y"
    try:
        datetime.datetime.strptime(date, fmt)
    except ValueError:
        print("Wrong date format! Should be MM-DD-YYYY")
        return

    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

    # check 4: if the vaccines are out of stock
    vname = tokens[2]
    vaccines = get_vaccine()
    try:
        if vaccines[vname] == 0:
            print(f"Vaccine {vname} is out of stock!")
            return
    except KeyError:
        print("No such vaccine, please try again!")
        return

    # check 5: if the caregivers are all reserved
    available_caregiver = get_schedule(d)
    if len(available_caregiver) == 0:
        print("No caregiver is available on that day!")
        return

    # check 6: if the patient has already had an appointment on that day
    if check_appointment_date(pname, date):
        return

    try:
        assigned_caregiver = random.choice(available_caregiver)  # randomly assign a caregiver
        appointment_id = random.randint(1000, 9999)  # randomly assign a 4-digit integer as the appointment ID

        # assign a new appointment ID if there exists a same one in the database
        while appointment_id_exists(appointment_id):
            appointment_id = random.randint(1000, 9999)

        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        # decrease the vaccine dose
        vaccine = Vaccine(vaccine_name=vname, available_doses=vaccines[vname]).get()
        vaccine.decrease_available_doses(num=1)

        # insert the appointment to DB
        add_appointment = "INSERT INTO Appointments VALUES (%d, %s, %s, %s, %s)"
        try:
            cursor.execute(add_appointment, (appointment_id, assigned_caregiver, pname, vname, d))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            print("Error occurred when inserting appointment")
            cm.close_connection()
        cm.close_connection()

        # update the caregiver's availability
        delete_availability(d, assigned_caregiver)

        print("Reservation success!")
        print(f"Your caregiver is {assigned_caregiver}, your appointment ID is {appointment_id}")
    except:
        print("Reservation failed, please try again!")
        return


def upload_availability(tokens):
    """This function upload caregiver's availability on the given date into the database."""
    # upload_availability <date>
    # check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return
    name = current_caregiver.username

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    # check 3: if the datetime format is correct
    date = tokens[1]
    fmt = "%m-%d-%Y"
    try:
        datetime.datetime.strptime(date, fmt)
    except ValueError:
        print("Wrong date format! Should be MM-DD-YYYY")
        return

    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

    # check 4: check if an appointment has already been scheduled on that day
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    check_app = "SELECT * FROM Appointments WHERE (Cusername = %s AND Time = %s)"
    try:
        cursor.execute(check_app, (name, d))
        if cursor.rowcount != 0:
            print("You have appointment on that day!")
            cm.close_connection()
            return
    except:
        print("Error occurred when checking appointments")
        cm.close_connection()
        return

    # upload availability
    try:
        try:
            current_caregiver.upload_availability(d)
        except:
            print("Upload Availability Failed")
            return
        print("Availability uploaded!")
    except ValueError:
        print("Please enter a valid date!")
        return
    except pymssql.Error as db_err:
        print("Error occurred when uploading availability")
        return


def cancel(tokens):
    """This function cancels the existing appointment for the given appointment ID."""
    # this function is too redundant and needs simplification
    global current_caregiver
    global current_patient
    # check 1: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    # check 2: if no one's already logged-in
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    # check 3: if input is an integer
    try:
        id = int(tokens[1])
    except:
        print("Please input a valid appointment ID!")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    # execute the cancelation for patient
    if current_caregiver is None and current_patient is not None:
        selected = "SELECT * FROM Appointments WHERE (Pusername = %s AND Id = %d)"
        name = current_patient.username
        try:
            cursor.execute(selected, (name, id))
            if cursor.rowcount == 0:
                print("Wrong ID, or you have nothing to cancel!")
                return
            else:
                # Update the caregiver's availability
                caregiver_avail = "SELECT Cusername, Time FROM Appointments WHERE (Pusername = %s AND Id = %d)"
                try:
                    cursor.execute(caregiver_avail, (name, id))
                    for row in cursor:
                        assigned_caregiver = row["Cusername"]
                        date = row["Time"]
                    add_availability(date, assigned_caregiver)
                except:
                    print("Error occurred when updating availability")
                    cm.close_connection()
                    return

                # Increase the vaccine dose
                vacc = "SELECT Vname FROM Appointments WHERE (Pusername = %s AND Id = %d)"
                try:
                    cursor.execute(vacc, (name, id))
                    for row in cursor:
                        vname = row["Vname"]
                    vaccines = get_vaccine()
                except pymssql.Error:
                    print("Error occurred when deleting appointments")
                    cm.close_connection()
                    return

                vaccine = Vaccine(vaccine_name=vname, available_doses=vaccines[vname]).get()
                vaccine.increase_available_doses(num=1)

                # Delete the appointment in DB
                delete = "DELETE FROM Appointments WHERE (Pusername = %s AND Id = %d)"
                try:
                    cursor.execute(delete, (name, id))
                    # you must call commit() to persist your data if you don't set autocommit to True
                    conn.commit()
                except pymssql.Error:
                    print("Error occurred when deleting appointments")
                    cm.close_connection()
                    return
                print(f"Appointment {id} has been successfully canceled!")
        except:
            print("Error occurred when canceling appointments")
            cm.close_connection()
            return
    # execute the cancelation for caregiver
    elif current_patient is None and current_caregiver is not None:
        selected = "SELECT * FROM Appointments WHERE (Cusername = %s AND Id = %d)"
        name = current_caregiver.username
        try:
            cursor.execute(selected, (name, id))
            if cursor.rowcount == 0:
                print("Wrong ID, or you have nothing to cancel!")
                return
            else:
                # Update the caregiver's availability
                caregiver_avail = "SELECT Cusername, Time FROM Appointments WHERE (Cusername = %s AND Id = %d)"
                try:
                    cursor.execute(caregiver_avail, (name, id))
                    for row in cursor:
                        assigned_caregiver = row["Cusername"]
                        date = row["Time"]
                    add_availability(date, assigned_caregiver)
                except:
                    print("Error occurred when updating availability")
                    cm.close_connection()
                    return

                # Increase the vaccine dose
                vacc = "SELECT Vname FROM Appointments WHERE (Cusername = %s AND Id = %d)"
                try:
                    cursor.execute(vacc, (name, id))
                    for row in cursor:
                        vname = row["Vname"]
                    vaccines = get_vaccine()
                except pymssql.Error:
                    print("Error occurred when deleting appointments")
                    cm.close_connection()
                    return

                vaccine = Vaccine(vaccine_name=vname, available_doses=vaccines[vname]).get()
                vaccine.increase_available_doses(num=1)

                # Delete the appointment in DB
                delete = "DELETE FROM Appointments WHERE (Cusername = %s AND Id = %d)"
                try:
                    cursor.execute(delete, (name, id))
                    # you must call commit() to persist your data if you don't set autocommit to True
                    conn.commit()
                except pymssql.Error:
                    print("Error occurred when deleting appointments")
                    cm.close_connection()
                    return
                print(f"Appointment {id} has been successfully canceled!")
        except pymssql.Error:
            print("Error occurred when canceling appointments")
            cm.close_connection()
            return
    else:
        print("Error occurred, please try again!")
        return

    cm.close_connection()


def add_doses(tokens):
    """This function adds the vaccine and corresponding doses into the database."""
    # add_doses <vaccine> <number>
    # check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = str(tokens[1])
    doses = int(tokens[2])
    if doses <= 0:
        print("Invalid input!")
        return

    vaccine = None
    try:
        try:
            vaccine = Vaccine(vaccine_name, doses).get()
        except:
            print("Failed to get Vaccine!")
            return
    except pymssql.Error:
        print("Error occurred when adding doses")
        return

    # check 3: if getter returns null, it means that we need to create the vaccine and insert it into the Vaccines
    #          table

    if vaccine is None:
        try:
            vaccine = Vaccine(vaccine_name, doses)
            try:
                vaccine.save_to_db()
            except:
                print("Failed To Save")
                return
        except pymssql.Error:
            print("Error occurred when adding doses")
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            try:
                vaccine.increase_available_doses(doses)
            except:
                print("Failed to increase available doses!")
                return
        except pymssql.Error:
            print("Error occurred when adding doses")
            return

    print("Doses updated!")


def show_appointments(tokens):
    """This function shows the appointment(s) for the logged-in user."""
    global current_caregiver
    global current_patient
    # check 1: the length for tokens need to be exactly 1 to include all information (with the operation name)
    if len(tokens) != 1:
        print("Please try again!")
        return

    # check 2: if no one's already logged-in
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    # show the appointment if login user is a patient
    if current_caregiver is None and current_patient is not None:
        show = "SELECT Id, Cusername, Vname, Time FROM Appointments WHERE Pusername = %s"
        name = current_patient.username
        try:
            cursor.execute(show, name)
            if cursor.rowcount == 0:
                print("You have not scheduled any appointments!")
                return
            else:
                for row in cursor:
                    id = row["Id"]
                    cname = row["Cusername"]
                    vname = row["Vname"]
                    date = row["Time"]
                    d = datetime.datetime.strftime(date, "%m-%d-%Y")
                    print(f"Appointment ID: {id}, Caregiver's name: {cname}, Vaccine: {vname}, Date: {d}")
        except pymssql.Error:
            print("Error occurred when showing appointments")
            cm.close_connection()
            return
    # show the appointment if login user is a caregiver
    elif current_patient is None and current_caregiver is not None:
        show = "SELECT Id, Pusername, Vname, Time FROM Appointments WHERE Cusername = %s"
        name = current_caregiver.username
        try:
            cursor.execute(show, name)
            if cursor.rowcount == 0:
                print("There is no appointments for you!")
                return
            else:
                for row in cursor:
                    id = row["Id"]
                    pname = row["Pusername"]
                    vname = row["Vname"]
                    date = row["Time"]
                    d = datetime.datetime.strftime(date, "%m-%d-%Y")
                    print(f"Appointment ID: {id}, Patient's name: {pname}, Vaccine: {vname}, Date: {d}")
        except pymssql.Error:
            print("Error occurred when showing appointments")
            cm.close_connection()
            return
    else:
        print("Error occurred, please try again!")
        return

    cm.close_connection()


def logout(tokens):
    """This function logs out the current logged-in user."""
    global current_patient
    global current_caregiver
    # check 1: the length for tokens need to be exactly 1 to include all information (with the operation name)
    if len(tokens) != 1:
        print("Please try again!")
        return

    # check 2: if no one's already logged-in
    if current_caregiver is None and current_patient is None:
        print("No one logged-in!")
        return
    else:
        current_patient = None
        current_caregiver = None

    # check 3: if the logout was successful
    if current_caregiver is not None or current_patient is not None:
        print("Please try again!")
    else:
        print("Logged-out!")


def start():
    """Execute the functions."""
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>")
        print("> reserve <date> <vaccine>")
        print("> upload_availability <date>")
        print("> cancel <appointment_id>")
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")
        print("> logout")
        print("> Quit")
        print()
        response = ""
        print("> Enter: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Type in a valid argument")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Try Again")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Thank you for using the scheduler, Goodbye!")
            stop = True
        else:
            print("Invalid Argument")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
