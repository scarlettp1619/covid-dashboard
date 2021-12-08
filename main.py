import ast  # Import library for reading json file
import threading  # Import library to allow repeated schedules
import sched  # Imports the scheduling library, allows for scheduling to occur
import time  # Imports the time library, this is used in scheduling to set the time when the scheduling occurs
import pytest  # Imports the pytest library, this is used for testing data in the covid data and news data modules
import logging  # Imports the logging library, this is used to log data in the logging file

import covid_data_handler
import covid_news_handling
from covid_data_handler import process_covid_csv_data, covid_API_request, format_cov_data, schedule_covid_updates, \
    schedule_covid_repeat  # Imports subroutines from the COVID data handler, this allows the API request to be called
# in the main file, along with processing the data (allows it to be displayed when called), and formatting the deaths
# and hospital cases correctly
from covid_news_handling import update_news, news_API_request, schedule_news_updates, schedule_news_repeat  # Imports
# subroutines from News handling, this allows the news API request to be called in the main file, along with processing
# the data (displaying it when called)
from flask import Flask, render_template, request, redirect  # Imports the flask library, which allows for the use of
# flask. This enables us to use HTML along with python - injecting code into the index.html file. render_template allows
# the index.html file to be displayed with flask, request allows to get data from the webpage using flask's GET method,
# and redirect allows the page to redirect the user back to itself when data is requested.
from datetime import datetime  # Imports datetime, this allows the system to get the current time for scheduling events

now = datetime.now()  # Gets the current time from the system
contents = open("config.json").read()  # Opens the config
dictionary = ast.literal_eval(contents)  # Converts the config file into a dictionary file to be read
logging.basicConfig(filename=dictionary["logging_file"], level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(filename)s: %(message)s")  # Initialises the logging file.
# sets formatting so date and time are shown when logging. File name is set to logging_file from the config
# default is logging.log
logging.debug("Config file opened successfully.")  # Logs the message to the logging file
local_location = dictionary["local_location"]  # Gets the local location from the config file (default Exeter)
location_type = dictionary["local_location_type"]  # Gets the local location type from the config file
national_location = dictionary["national_location"]  # Gets the national location from the config file (default England)
image = dictionary["image"]  # Gets the image file name from the config file
api_key = dictionary["api_key"]
testing = dictionary["automatic_testing"]
if api_key == "":  # If no API key has been entered
    print("NO API KEY HAS BEEN ENTERED. PLEASE ENTER A VALID API KEY IN THE CONFIG.JSON FILE FOR THIS PROGRAM TO WORK.")
    logging.debug("NO API KEY HAS BEEN ENTERED. PLEASE ENTER A VALID API KEY IN THE CONFIG.JSON FILE FOR" +
                  " THIS PROGRAM TO WORK.")
    exit()  # Exits the program
logging.debug("Config file read successfully.")
removed_titles, updates, ls = [], [], []  # Declares variables for later use. These declare any titles that will be
# removed, and any updates that are removed
covid_API_request(local_location, location_type)  # Requests data from the COVID API. This passes arguments from the
# config to grab the csv from the government API, allowing it to be displayed on the system
try:
    news_API_request(removed_titles)  # Requests data from the news API, the data is returned as a json. removed_titles
    # is passed to calculate any new articles that need to be displayed when an update is scheduled. This is done by
    # adding the number of removed articles to the number of articles that should display (default 5)
    news = update_news(removed_titles)  # Stores news data in news
except KeyError:  # If news update fails (API key is wrong or news API has failed)
    print("INVALID API KEY HAS BEEN ENTERED. PLEASE ENTER A VALID API KEY IN THE CONFIG.JSON FILE FOR THIS PROGRAM" +
          " TO WORK.")
    logging.debug("INVALID API KEY HAS BEEN ENTERED. PLEASE ENTER A VALID API KEY IN THE CONFIG.JSON FILE FOR" +
                  " THIS PROGRAM TO WORK.")
    exit()  # Exits the program
s = sched.scheduler(time.time, time.sleep)  # Initialises the scheduler to allow for scheduled events
if testing == "True":
    pytest.main(["-v", "covid_data_handler.py"])  # Runs the COVID test data at the very start of the program. This is
    # repeated every minute
    pytest.main(["-v", "covid_news_handling.py"])  # Runs the news test data at the very start of the program. This is
    # repeated every minute


def hhmm_to_seconds(hhmm):  # Subroutine for converting HH:MM:SS time from the website into seconds
    return sum([a * b for a, b in zip([3600, 60, 1], map(int, hhmm.split(':')))])  # Since the data from the website is
    # displayed as HH:MM, this splits the string by the delimiter ":" and multiplies the hours by 3,600 (H -> M -> S)
    # and the minutes by 60 (M -> S). Any seconds entered are multiplied by 1. This is because the time from datetime
    # is displayed as HH:MM:SS (ex. 23:11:00). Not multiplying the seconds by 1 causes improper formatting and the
    # scheduling won't work correctly


def schedule_covid_test():
    if testing == "True":
        update_interval = int(dictionary["update_covid_test"])  # Sets the update interval for the scheduled covid test.
        # This is set in config.json default 60 seconds
        s.enterabs(time.time() + update_interval, 1, pytest.main, (["-v", "covid_data_handler.py"],))  # Enters the
        # update into the scheduler at the set update interval.
        threading.Timer(update_interval, schedule_covid_test).start()  # Creates a thread so the test can be carried out
        # at the same interval.


def schedule_news_test():
    if testing == "True":
        update_interval = int(dictionary["update_news_test"])  # Sets the update interval for the scheduled news test.
        # This is set in the config.json default 60 seconds
        s.enterabs(time.time() + update_interval, 1, pytest.main, (["-v", "covid_news_handling.py"],))  # Enters the
        # update into the scheduler at the set update interval.
        threading.Timer(update_interval, schedule_news_test).start()  # Creates a thread so the test can be carried out
        # at the same interval.


def repeating_updates(update_label):  # Function to prevent the same update name from being entered into the system
    # twice. If you were to enter multiple updates with the name "update", it'd add a number on the end of it
    # (ex "update", "update-1", "update-2")
    num = 0  # Sets a default value to append to the end of a name. If there are no repeats, this will remain as 0
    while update_label in ls:  # Checks through the list of update names. If it exists, it'll carry through the code.
        # if not, then the update is added to the list normally
        if num == 0:  # If this is the first instance of a repeated name
            num = 1  # Sets suffix to 1 (ex. "update-1")
            update_label += "-" + str(num)  # Appends the number to the update name
        else:  # If this is not the first instance of a repeated name
            update_increment = update_label.split('-')  # Splits the update name by the delimiter "-" (prevents stuff
            # like "update-1-1" happening)
            update_increment[-1] = str(int(update_increment[-1]) + 1)  # Since splitting a string converts it into a
            # list of items, this gets the final value of the list and adds 1 to it. This is to ensure random numbers
            # aren't incremented (ex. entering "update-1-1" twice should return "update-1-1" and "update-1-2", not
            # "update-1-1" and "update-2-1").
            update_label = '-'.join(update_increment)  # Joins the list back into a string to display the new name
    ls.append(update_label)  # Appends the name to a list in cache, this is so update names aren't reset after the
    # subroutine ends


def remove_title(title_remove):  # Function to remove update names from displaying on the website
    dict_remove = {
        "title": title_remove
    }  # Creates a dictionary with one key ("title") which can be used to remove data from the website. This is done
    # because the data on the website must be entered with a dictionary
    global updates  # Calls updates as a global variable, this allows it to be changed in the function as well as the
    # program as a whole
    updates = [d for d in updates if d['title'] != dict_remove['title']]  # Iterates through the entire updates
    # dictionary list and re-writes it without the matching removed dictionaries
    ls.remove(title_remove)  # Removes the update name from the temporary list. This is to prevent stuff like
    # "update-3" and "update-4" displaying after "update-2" has already been removed
    logging.debug("'%s" % title_remove + "' has been removed from updates.")


app = Flask(__name__)  # Initialising the Flask app


@app.route(dictionary["redirect"])  # Routes the Flask app to the main page of the config file (default "index.html")
def index():  # Subroutine for everything displayed on the index page
    global news  # Declares news as a global variable so it can be changed throughout the module
    news = update_news(removed_titles)  # Stores news data
    deaths, hospital_cases, new_cases, seven_day_cases_l, seven_day_cases = process_covid_csv_data()
    # This processes all of the data that was grabbed from the API, putting it into the necessary variables. These are
    # all calculated within the data handler class
    total_deaths = format_cov_data(deaths)  # Processes the deaths that have been stored in memory, this formats it so
    # it can be displayed correctly on the website
    new_hospital_cases = format_cov_data(hospital_cases)  # Processes hospital cases that have been stored in memory,
    # this formats it so it can be displayed correctly on the website
    update_time = request.args.get("update")  # Gets the update time selected when scheduling an update in the website,
    # stored as "HH:MM" string
    covid_data_handler.run_updates()  # Run COVID data scheduled events
    covid_news_handling.run_updates()  # Run news
    s.run(blocking=False)  # Run any scheduled events
    if update_time == "":  # If an update time is not entered
        logging.warning("User didn't enter update time. Update cancelled")
        return redirect(request.path)  # Redirect back to index page
    if request.args.get("notif"):  # If a news box is closed
        title_add = str(request.args.get("notif"))  # Grab the title of the news box from the website
        dict_add = {
            "title": title_add
        }  # Creates a dictionary with one key ("title") which can be used to remove news from the website. This is done
        # because the news on the website must be entered with a dictionary
        removed_titles.append(dict_add)  # Adds the removed article to a list of dictionaries so it won't be displayed
        # after an update is performed. removed_titles is called in the news API and the processing of the news
        news = update_news(removed_titles)  # Re-displays the news on the page without any removed articles
        logging.debug("User removed news article '%s" % title_add + "'.")
        return redirect(request.path)  # Redirect back to the index page (updates the news articles)
    if request.args.get("update_item"):  # If an update is cancelled
        title_remove = str(request.args.get("update_item"))  # Gets the name of the update from the website
        remove_title(title_remove)  # Calls the remove_title function to remove it from the update list. Updates can't
        # actually be removed from the scheduler after they are run using s.run(), so this is only on the front-end
        logging.debug("User removed update '%s" % title_remove + "'.")
        return redirect(request.path)  # Redirect back to the index page (updates the update list)
    if request.args.get("two"):  # When the schedule update button is pressed
        current_time = now.strftime("%H:%M:%S")  # Gets the current time in HH:MM format
        update_label = str(request.args.get("two"))  # Gets the name of the update entered in the label on the website
        # to be added to the scheduler
        delay = (hhmm_to_seconds(update_time) - hhmm_to_seconds(current_time))  # Calculates how long
        # until the scheduled event is going to take place by taking the current time. This converts each time format
        # (HH:MM) for update_time and current_time into seconds
        if delay < 0:  # If update_time - current_time is less than zero (this can happen when the user selects a time
            # before the current time)
            delay *= -1  # Multiplies the scheduling time by -1, turning the negative value, positive. This ensures a
            # 24 hour time frame can be utilised for scheduling updates
        if request.args.get("covid-data"):  # If the user selects to update covid data
            repeating_updates(update_label)  # Checks if any instances of the update name already exists
            new_label = ls[-1]  # Rewrites the update name in instances where it does
            if request.args.get("repeat"):  # If the user selects the repeat box
                if delay == 0:  # If the delay is set to 0 seconds (the update time is the same as the current time)
                    return redirect(request.path)  # Redirects back to the index page. This is done so the schedule time
                # can not be set to zero. If this happens, an infinite loop of scheduled updates will occur, crashing
                # the program. This is only needed for repeated updates
                schedule_covid_repeat(delay, new_label, ls)  # Calls the repeating update function for COVID updates
                # with arguments for the specified delay time and name of update
                s.enter(delay + 1, 1, remove_title, [new_label, ])  # Schedules an update to remove the update from the
                # update list once the event has been carried out
                dict_add = {
                    "title": new_label,
                    "content": dictionary["covid_repeat"] + "%s" % update_time
                }  # Adds the name of update and schedule time to a dictionary. This allows the data to be displayed on
                # the website, as it will only process dictionaries
                logging.debug("Repeating COVID data update '%s " % str(new_label) + "' has been entered for %s"
                              % str(update_time) + " every 24 hours.")
            else:  # If the user does not select the repeat box
                schedule_covid_updates(delay, new_label, ls)  # Calls the update function for COVID updates with
                # arguments for the specified delay time and name of update
                s.enter(delay + 1, 1, remove_title, [new_label, ])
                dict_add = {
                    "title": new_label,
                    "content": dictionary["covid_update"] + "%s" % update_time
                }  # Adds the name of update and schedule time to a dictionary. Reasoning explained above
                logging.debug("COVID data update '%s " % str(new_label) + "' has been entered for %s" % str(
                    update_time) + ".")
            updates.append(dict_add)  # Appends the update to the update list to be displayed on the website
        if request.args.get("news"):  # If the user selects to update news data (separate if statements are used to

            """
            # A lot of this has already been explained above with COVID updates, so no explanation will be provided
            # here. It is the exact same thing.
            """

            repeating_updates(update_label)
            new_label = ls[-1]
            if request.args.get("repeat"):
                if delay <= 0:
                    return redirect(request.path)
                delay = round(delay / 60) * 60
                schedule_news_repeat(delay, new_label, removed_titles, ls)  # Calls the update function for
                # repeated news updates
                s.enter(delay + 1, 1, remove_title, [new_label, ])
                dict_add = {
                    "title": new_label,
                    "content": dictionary["news_repeat"] + "%s" % update_time
                }  # Adds the name of update and schedule time to a dictionary for news updates
                logging.debug("Repeating news data update '%s " % new_label + "' has been entered for %s"
                              % update_time + " every 24 hours.")
            else:
                schedule_news_updates(delay, new_label, removed_titles, ls)  # Calls the update function for
                # news updates
                s.enter(delay + 1, 1, remove_title, [new_label, ])
                dict_add = {
                    "title": new_label,
                    "content": dictionary["news_update"] + "%s" % update_time
                }  # Adds the name of update and schedule time to a dictionary for news updates
                logging.debug("News data update '%s " % new_label + "' has been entered for %s" % update_time + ".")
            updates.append(dict_add)
        return redirect(request.path)  # Redirects back to index page. Updates any changes made
    return render_template(dictionary["template"], location=local_location, local_7day_infections=
    "{:,}".format(int(seven_day_cases_l)),
                           nation_location=national_location, national_7day_infections=
                           "{:,}".format(int(seven_day_cases)),
                           image=image, hospital_cases=
                           dictionary["hospital_cases"] + "%s" % "{:,}".format(int(str(new_hospital_cases))),
                           deaths_total=
                           dictionary["deaths_total"] + "%s" % "{:,}".format(int(str(total_deaths))),
                           news_articles=news, updates=reversed(updates))
    # This return statement displays all the data on the website. Information about the arguments taken can be found
    # in the main html file. All variables here have already been declared and described earlier in the file.
    # "{:,}".format(int(value)) formats numbers with commas (ex. "500,000" instead of "500000)


@app.route("/")  # Routing for the default page ("/"), or http://127.0.0.1:5000/ during development
def landing():  # Subroutine for landing on the default page
    return redirect(dictionary["redirect"])  # Redirects the user to the home page in the json


if __name__ == "__main__":
    app.run()  # Runs the Flask app
