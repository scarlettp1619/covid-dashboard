---------------------------------
    SCARLETT PARKER ECM1400
PROGRAMMING CONTINUOUS ASSESSMENT
---------------------------------

MAIN INFO

    This Python project contains a COVID-19 dashboard developed using Flask. Live COVID updates and news updates
    are grabbed from the news API (newsapi.org) and UK COVID-19 API. FOR THE DASHBOARD TO WORK YOU MUST ENTER A
    VALID API KEY. REGISTER AT http://newsapi.org - THE CONFIG.JSON HAS A DEFAULT KEY BUT THIS ONLY HAS LIMITED
    USES. IF A KEY IS INVALID OR EMPTY, THE PROGRAM WON'T RUN.


CONFIG FILE

    In the config file there are many arguments that can change the information displayed on the website. Beware,
    editing this file may cause the system to crash if done improperly, so edit at your own risk.

    "local_file" - name of the file for local COVID data (default: "local_data.csv")

    "national_file" - name of the file for national COVID data (default: "national_data.csv")

    "news_file" -  name of the file for news data (default: "news_data.json")

    "local_location" - location of local COVID data (default: "Exeter")

    "local_locaion_type" - location type for local COVID data (default: "ltla")

    "national_location" - location of national COVID data (default: "England")

    "national_location_type" - location type for national COVID data (default: "nation")

    "image" - image displayed on the page (default: "matt.gif")

    "page_size" - number of news articles displayed on the page at once (default: "5")

    "max_page_size" - maximum number of news articles displayed on the page at once (default: "5") - WARNING - 

    changing this value above "100" may crash the program as it exceeds the maximum number of news API requests

    "covid_terms" - terms that news API searches for (separated by spaces, default: "Covid COVID-19 Coronavirus")

    "api_key" - news API key required to search (default: "ab1e69378ee3438c9e9c706bb8a83327")
    
    "sort_by" - sorting for news API search (default: "popularity")

    "covid_update" - display for COVID updates (default: "COVID update at ")

    "covid_repeat" - display for repeating COVID updates (default: "COVID update every day at ")

    "news_update" - display for news updates (default: "News update at ")

    "news_repeat" - display for repeating news updates (default: "News update every day at ")

    "hospital_cases" - display for hospital cases (default: "Current hospital cases: ")

    "deaths_total" - display for total deaths (default: "Total deaths: ")

    "template" - main page that Flask runs on (default: "index.html") - WARNING - changing this value may crash the program

    "redirect" - page that Flask will automatically redirect to (default: "/index") - WARNING - changing this value may
    crash the program

    "update_news_test" - how often testing is carried out for news in seconds (default: "60")

    "update_covid_test" - how often testing is carried out for COVID data seconds (default: "60")

    "logging_file" - where data is logged to (default: "logging.log")

    "automatic_testing" - whether testing is carried out by pytest automatically or not (default: "False")
    (can only be changed to either "True" or "False")

RUNNING THE SYSTEM

    To run the system simply start main.py. Some libraries are required to run the system, these can be installed
    with pip or your IDE (if there's support for it).

3RD PARTY LIBRARIES NEEDED

    . pytest
    . uk-covid19
    . flask
    . requests
    