import requests
from copy import deepcopy as cp

url = "http://127.0.0.1:5000"

# put necessary data in database for test

EXAMPLE_SONG = {
    "title": "Song Title",
    "author": "Song Author",
    "songId": "12345678",
    "emailAddress": "some.email@gmail.com",
    "lines": [
        { "text": "Slide 1 Line 1", "divider": False, },
        { "text": "Slide 1 Line 2", "divider": False, },
        { "text": "Slide 1 Line 3", "divider": False, },
        { "text": "Slide 1 Line 4", "divider": True,  },
        { "text": "Slide 2 Line 1", "divider": False, },
        { "text": "Slide 2 Line 2", "divider": False, },
        { "text": "Slide 2 Line 3", "divider": False, },
        { "text": "Slide 2 Line 4", "divider": True,  },
        { "text": "Slide 3 Line 1", "divider": False, },
        { "text": "Slide 3 Line 2", "divider": False, },
        { "text": "Slide 3 Line 3", "divider": False, },
        { "text": "Slide 3 Line 4", "divider": True,  },
    ],
    "slides": [
        [
            "Slide 1 Line 1",
            "Slide 1 Line 2",
            "Slide 1 Line 3",
            "Slide 1 Line 4",
        ],
        [
            "Slide 2 Line 1",
            "Slide 2 Line 2",
            "Slide 2 Line 3",
            "Slide 2 Line 4",
        ],
        [
            "Slide 3 Line 1",
            "Slide 3 Line 2",
            "Slide 3 Line 3",
            "Slide 3 Line 4",
        ],
    ],
    "settings": {
        "textColor": "#ffffff",
        "backgroundColor": "#000000",
        "numberOfColumns": 5,
        "fontSize": 36,
        "fontFamily": "Arial",
        "includeTitleSlide": "true"
    },
}

song = cp(EXAMPLE_SONG)

# requests.post(url + "/save", song)
