## Overview
Tired of constantly checking different university or company websites to see if they've added or removed any open positions? Then this simple GUI application may be for you!
I developed JobCheckerGUI to have a quick and easy way of checking whether or not a university department had updated their faculty job openings page.
The function is quite simple: in the main table, you enter labels (e.g. a university/company and its department) and the URL corresponding to the webpage where they post jobs. The package BeautifulSoup is used to parse the page and store the text response. It then compares this parsed text with the previous response (stored in a .pickle file) and lets you know whether or not the text on the page has been updated.
In its current implementation, the application is sensitive to any text change that occurs, and is not specific to keywords. But I've still found it useful, and hope you will too!

## Project Structure
JobCheckerGUI/
│
├── app/
│   ├── __init__.py
│   ├── main_window.py        # Contains the MainWindow class
│   ├── worker_thread.py      # Contains the WorkerThread class
│   └── utils.py              # Contains utility functions
│
├── ui/
│   └── JobCheckerGUI.ui      # UI file created with Qt Designer
│
├── data/
│   └── labels_and_urls.py    # Data file containing labels and URLs
│
├── resources/
│   └── previous_responses.pickle  # Previously saved responses
│
├── config/
│   ├── __init__.py
│   ├── config_manager.py     # Contains the ConfigManager class
│   └── dataTable_config.pickle   # Configuration file for the data table
│
├── run.py                    # Script to run the application
├── requirements.txt          # Dependencies file (optional)
├── LICENSE                   # License file
└── README.md                 # README file
