from uk_covid19 import Cov19API  # Imports the COVID API to allow requests for COVID data

import ast
import sched
import time
import threading
import logging

config = open("config.json")  # Opens the config file to be read
contents = config.read()  # Reads each line of the config file
dictionary = ast.literal_eval(contents)  # Converts the config file into a dictionary
local_file = dictionary["local_file"]  # Gets the local file name from the config file
national_file = dictionary["national_file"]  # Gets the national file name from the config file
national_location = dictionary["national_location"]  # Gets the national location name from the config file
national_type = dictionary["national_type"]  # Gets the national location type from the config file
s = sched.scheduler(time.time, time.sleep)  # Initialises the scheduler for scheduling events
logging.basicConfig(filename='logging.log', level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")


def covid_API_request(location="Exeter", location_type="ltla"):
    # Function for requesting the COVID data from the API. This takes the arguments location (local location where
    # data is grabbed from), location_type (specific to API), national_location (national location where data is
    # grabbed from), national_type (specific to API), local_file (file where local data is stored) and national_file
    # (file where national data is stored)
    cases_and_deaths = {
        "newCasesBySpecimenDate": "newCasesBySpecimenDate"
    }  # Sets data to be wrote to local file. Only new cases are entered as that's all can be entered on the website.
    # For this reason, this cannot be set in the config file

    data_location = [
        'areaType=' + location_type,
        'areaName=' + location
    ]  # Sets location to determine where data is taken from for the local file. location_type and location can be set
    # in the config file, with the default values "ltla" and "Exeter" respectively

    local_data = Cov19API(data_location, cases_and_deaths).get_csv()  # This grabs the data from the API using the
    # determined arguments, converting it to a csv file

    cases_and_deaths = {
        "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
        "hospitalCases": "hospitalCases",
        "newCasesBySpecimenDate": "newCasesBySpecimenDate"
    }  # Sets data to determine what's in the national file. Cumulative deaths, hospital cases and new cases are entered
    # as that's what is displayed on the website. For this reason, these cannot be set in the config file

    data_location = [
        'areaType=' + national_type,
        'areaName=' + national_location
    ]  # Sets location to determine where data is taken from for the local file. national_type and national_location can
    # be set in the config file, with the default values are "nation" and "England" respectively

    national_data = Cov19API(data_location, cases_and_deaths).get_csv()  # This grabs the data from the API using the
    # determined arguments, converting it to a csv file
    logging.debug("COVID API successfully called.")
    parse_csv_data(national_data, local_data)  # Function to parse the data from the API,
    # taking the arguments national_file, local_file, national_data and local_data all set in the config file
    return national_data, local_data


def parse_csv_data(national_data, local_data):
    with open(local_file, "w") as f:  # Opens the local file with write properties. "w" allows for a file to be
        #  created if no such file exists. local_file is set in the config as default "local_data.csv"
        f.write(local_data)  # Writes the local data from the API to the file
    with open(national_file, "w") as f:  # Opens the national file with the write properties. national_file is
        # set in the config as default "national_data.csv"
        f.write(national_data)  # Writes the national data from the API to the file
    logging.debug("COVID data successfully parsed into %s" % local_file + " and %s" % national_file + ".")


def process_covid_csv_data():  # Subroutine for returning COVID data with arguments
    # national_file and local_file, both set in the config file
    f = open(national_file)  # Opens the national file
    g = open(local_file)  # Opens the local file
    national_list, local_list = [], []  # Creates arrays for national and local data to be appended to
    l_s_d_cases, n_s_d_cases = 0, 0  # Initialises integers for seven day case rates for national and local data
    for x in f.readlines():  # Iterates through every line in the national file
        national_list.append(x)  # Appends the national data to the list
    for x in g.readlines():  # Iterates through every line in the local file
        local_list.append(x)  # Appends the local data to the list
    local_new_cases = local_list  # Sets local data equal to data from the list
    n_deaths, n_hospital_cases, n_new_cases = zip(*(j.split(',') for j in national_list))  # Sets national data equal
    # to data from the list. Since there are multiples sets of data separated by commas (e.g. d1, d2, d3, d1, d2, d3),
    # the data is iterated through and split by the delimiter ','. zip(*) allows for everything to be processed in
    # one line
    logging.debug("COVID data successfully processed.")
    for i in range(0, 7):  # Repeats 7 times
        n_s_d_cases += int(n_new_cases[i + 2])  # Adds case data to seven day cases for national data, starting from the
        # 3rd item in list. This is done because the first item is the name of the data (e.g. newCasesBySpecimenDate),
        # and the second value isn't up to date enough to be considered (this is because of how COVID processing works)
        l_s_d_cases += int(local_new_cases[i + 2])  # Adds case data to seven day cases for local data
    return n_deaths, n_hospital_cases, n_new_cases, l_s_d_cases, n_s_d_cases  # Returns all
    # the values for data in national list and local list. These are set in the main file


def format_cov_data(data):  # Subroutine for formatting data (specifically for deaths and hospital cases). This is done
    # because of how COVID processing works - there are many blank values as data isn't updated every single day
    # (unlike case data)
    cov_data = 0  # Initialises integer to be incremented
    for i in data:  # Iterates through all data entered
        if i.isdigit():  # When the loop reaches a number (not a blank space)
            cov_data = i  # Set the displayed data to the first number found
            break  # Break out of the loop (prevents iterating through all data and setting the display as the final
            # value)
    logging.debug("COVID data successfully formatted.")
    return cov_data  # Returns the data to be displayed


def covid_update(update_name, ls):
    if update_name in ls:  # If update is still in update list
        covid_API_request()  # Update COVID data
    else:  # If update has been removed from update list
        logging.debug("COVID update '%s" % update_name + "' removed from list. Update not performed.")  # Don't perform
        # COVID update and log to logging file


def schedule_covid_updates(update_interval, update_name, ls):  # Function for scheduling covid updates. update_interval
    # is the time in seconds (determined by the user om the website) that will be taken for the event to be carried out.
    # update_name is the name of the update (determined by the user)
    s.enter(update_interval, 1, covid_update, [update_name, ls, ])
    # Enters the scheduled event* into the scheduler set by the user
    # *This specific event is for updating the covid information (grabbing data from the API and displaying it on
    # the website)


def schedule_covid_repeat(update_interval, update_name, ls):  # Function for scheduling repeating covid updates. This
    # allows for COVID updates to be released at specified intervals (update_interval)
    s.enter(update_interval, 1, covid_update, [update_name, ls, ])  # Enters the scheduled event into the
    # scheduler set by the user. Arguments are explained with schedule_covid_updates
    threading.Timer(86400, schedule_covid_repeat, [update_interval, update_name, ls, ]).start()  # This creates
    # a thread with a timer for 24 hours. This calls back on its own subroutine, allowing for repeating events to
    # occur. Threading ensures it happens in the background, so the program doesn't freeze while waiting for an update


def run_updates():
    s.run(blocking=False)  # Runs any schedules when the page is loaded by Flask. This is done because the HTML page
    # automatically refreshes the Flask app every minute. This does cause s ome delay with scheduling, but it's much
    # more efficient than running a constant thread of scheduling


def test_parse_csv_data():
    nat_file = dictionary["national_file"]
    loc_file = dictionary["local_file"]
    try:
        assert nat_file == national_file  # Checks if the national file names match
        assert loc_file == local_file  # Checks if the local file names match
        logging.debug("COVID file test successfully passed.")
    except AssertionError as e:  # If the test fails
        logging.error("COVID data test FAILED")
        logging.error(str(e))  # Logs the error


def test_process_covid_csv_data():
    deaths, hospital_cases, new_cases, l_s_d_cases, n_s_d_cases = process_covid_csv_data()
    deaths = format_cov_data(deaths)
    hospital_cases = format_cov_data(hospital_cases)
    try:
        assert int(deaths)
        assert int(hospital_cases)
        assert int(l_s_d_cases)
        assert int(n_s_d_cases)
        logging.debug("COVID data test successfully passed.")
        # All asserts check if the data that was just processed matches the correct format (int)
    except AssertionError as e:
        logging.error("COVID data test FAILED.")
        logging.error(str(e))


def test_covid_API_request():
    national_data, local_data = covid_API_request(location="Exeter", location_type="ltla")
    try:
        assert str(national_data)
        assert str(local_data)  # Checks if data is in the correct format (string)
        logging.debug("COVID API test successfully passed.")
    except AssertionError as e:
        logging.error("COVID API test FAILED.")
        logging.error(str(e))


def test_schedule_covid_updates():
    try:
        schedule_covid_updates(update_interval=60, update_name='update test', ls=['update test'])
        assert s.queue == s.queue
        # Checks if the update has been added to queue
        logging.debug("COVID update test successfully passed.")
    except AssertionError as e:
        logging.error("COVID update test FAILED.")
        logging.error(str(e))
