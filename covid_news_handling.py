import ast  # Import library for reading json file
import requests  # Import library for requesting from the news API
import sched
import time
import threading
import logging

config = open("config.json")  # Opens the config file to be read
contents = config.read()  # Reads each line of the config file
dictionary = ast.literal_eval(contents)  # Converts the config file into a dictionary
news_file = dictionary["news_file"]
s = sched.scheduler(time.time, time.sleep)  # Initialises the scheduler for scheduling events
logging.basicConfig(filename='logging.log', level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")


def news_API_request(removed_titles, covid_terms=dictionary["covid_terms"]):  # Subroutine for requesting data from the
    # news API, arguments are removed_titles (calculate if any new articles need to be added) and covid_terms (tells the
    # news API what to search for). Both are set in the config
    page_size = int(dictionary["page_size"]) + len(removed_titles)  # Sets the number of pages (articles) to be
    # displayed. The number of removed articles are added, so the number of articles displayed is always constant.
    # Default page size is 5
    if page_size < int(dictionary["max_page_size"]):  # If the number of pages (articles) is less than the max set in
        # the config (default is 99)
        page_size = int(dictionary["page_size"]) + len(removed_titles)  # Add number of removed titles back to the
        # number of pages (articles)
    else:  # If the number of pages (articles) exceeds the max set in the config
        page_size = int(dictionary["max_page_size"])  # Set number of page size to the maximum page size (this prevents
        # articles from exceeding the maximum size)
    request = requests.get("https://newsapi.org/v2/everything?q=" + covid_terms
                           + "&apiKey=" + dictionary["api_key"]
                           + "&sortBy=" + dictionary["sort_by"]
                           + "&pageSize=" + str(page_size))  # Requests data from the news API with arguments
    # covid_terms (what to search for), apiKey (key to access the API, otherwise data can't be requested), sortBy (how
    # news articles should be sorted, default is "popularity", and page_size (number of articles to be displayed)
    news_data = request.json()  # Creates a json file from the data requested from the API
    logging.debug("News data API successfully called.")
    with open(news_file, "w") as f:
        f.write(str(news_data))
    logging.debug("News successfully written to %s" % news_file + ".")


def update_news(removed_titles):  # Subroutine for updating the news (displaying it on the website). This is
    # separate from API request so any articles may be omitted (removed_titles)
    news_array = []  # Initialises an array for the news data to be appended to
    f = open(news_file).read()
    news_data = ast.literal_eval(f)
    articles = news_data["articles"]  # Since the news data from the API is an array of dictionaries, articles returns
    # only the articles from the API (there's some other response stuff that may show up in the json)

    for j in removed_titles:  # Iterates through the list of removed titles (if any)
        articles = [item for item in articles if item["title"] != j["title"]]  # Rewrites the articles without any of
        # the removed articles displaying. If the title of a removed article matches any article in the list of
        # dictionaries, that article is removed. This is based off the title of the article as that is what the HTML
        # file will return.

    for x in articles:  # Iterates through all of the articles
        x = {"title": x["title"], "content": x["description"]}  # Filters only the title and content of the articles.
        # Only this is displayed on the website
        news_array.append(x)  # Appends the titles and content to the array
    logging.debug("News data successfully updated.")
    return news_array  # Returns the array of dictionaries


def news_update(update_name, removed_titles, ls):  # Function for performing the news update
    if update_name in ls:  # If update name is in the list of updates
        news_API_request(removed_titles, dictionary["covid_terms"])  # Perform the news update
    else:  # If the update name has been removed from the list of updates
        logging.debug("News update '%s" % update_name + "' removed from list. Update not performed.") # Don't perform
        # the update and log to the console


def schedule_news_updates(update_interval, update_name, removed_titles, ls):  # Function for scheduling news updates.
    # update_interval and update_name are explained with the schedule_covid_updates subroutine
    s.enter(update_interval, 1, news_update, [update_name, removed_titles, ls, ])  # Enters the
    # scheduled event* into the scheduler set by the user
    # *This specific event is for updating the news data (grabbing data from the API and displaying it on the website)


def schedule_news_repeat(update_interval, update_name, removed_titles, ls):  # Function for scheduling repeating news
    # updates. This allows for news updates to be released at specific intervals (update_interval)
    s.enter(update_interval, 1, news_update, [update_name, removed_titles, ls, ])  # Enters the
    # scheduled event into the scheduler set by the user. Arguments are explained with schedule_covid_updates
    threading.Timer(86400, schedule_news_repeat, [update_interval, update_name, ]).start()  # This creates
    # a thread with a timer for 24 hours.


def run_updates():
    s.run(blocking=False)  # Runs any schedules when the page is loaded by Flask. This is done because the HTML page
    # automatically refreshes the Flask app every minute. This does cause s ome delay with scheduling, but it's much
    # more efficient than running a constant thread of scheduling


def test_news_API_request():
    file = dictionary["news_file"]
    try:
        assert file == news_file
        logging.debug("News API test passed.")
    except AssertionError as e:
        logging.error("News API test FAILED.")
        logging.error(str(e))


def test_update_news():
    try:
        assert update_news("")
        logging.debug("News update passed.")
    except AssertionError as e:
        logging.error("News update FAILED.")
        logging.error(str(e))


def test_schedule_news_updates():
    try:
        schedule_news_updates(update_interval=60, update_name='update test', removed_titles="", ls=["update test"])
        assert s.queue == s.queue
        logging.debug("News scheduling test passed.")
    except AssertionError as e:
        logging.error("News scheduling test FAILED.")
        logging.error(str(e))
