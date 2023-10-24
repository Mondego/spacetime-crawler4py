ABOUT
-------------------------
Greg Khanoyan - gkhanoya - 55544104

Adit Mohindra - amohind1 - 11539047

This is the base implementation of a full crawler that uses a spacetime
cache server to receive requests.

CONFIGURATION
-------------------------

### Step 1: Install dependencies

If you do not have Python 3.6+:

Windows: https://www.python.org/downloads/windows/

Linux: https://docs.python-guide.org/starting/install3/linux/

MAC: https://docs.python-guide.org/starting/install3/osx/

Check if pip is installed by opening up a terminal/command prompt and typing
the commands `python3 -m pip`. This should show the help menu for all the 
commands possible with pip. If it does not, then get pip by following the
instructions at https://pip.pypa.io/en/stable/installing/

To install the dependencies for this project run the following two commands
after ensuring pip is installed for the version of python you are using.
Admin privileges might be required to execute the commands. Also make sure
that the terminal is at the root folder of this project.
```
python -m pip install packages/spacetime-2.1.1-py3-none-any.whl
python -m pip install -r packages/requirements.txt
```

### Step 2: Configuring config.ini

Set the options in the config.ini file. The following
configurations exist.

**USERAGENT**: Set the useragent to `IR F19 uci-id1,uci-id2,uci-id3`. 
It is important to set the useragent appropriately to get the credit for 
hitting our cache.

**HOST**: This is the host name of our caching server. Please set it as per spec.

**PORT**: This is the port number of our caching server. Please set it as per spec.

**SEEDURL**: The starting url that a crawler first starts downloading.

**POLITENESS**: The time delay each thread has to wait for after each download.

**SAVE**: The file that is used to save crawler progress. If you want to restart the
crawler from the seed url, you can simply delete this file.

**THREADCOUNT**: This can be a configuration used to increase the number of concurrent
threads used. Do not change it if you have not implemented multi threading in
the crawler. The crawler, as it is, is deliberately not thread safe.


### Step 3: Define your scraper rules.

Develop the definition of the function scraper in scraper.py

```
def scraper (url: str, resp: utils.response.Response): -> list
    pass
```

The scraper takes in two parameters:

**ARGS**

*url*:

The URL that was added to the frontier, and downloaded from the cache.
It is of type str and was an url that was previously added to the
frontier.

*resp*:

This is the response given by the caching server for the requested URL.
The response is an object of type Response (see utils/response.py)
```
class Response:
    Attributes:
        url:
            The URL identifying the response.
        status:
            An integer that identifies the status of the response. This
            follows the same status codes of http.
            (REF: https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html)
            In addition there are status codes provided by the caching
            server (600-606) that define caching specific errors.
        error:
            If the status codes are between 600 and 606, the reason for
            the error is provided in this attribute. Note that for status codes
            (400-599), the error message is not put in this error attribute; instead it
            must picked up from the raw_response (if any, and if useful).
        raw_response:
            If the status is between 200-599 (standard http), the raw
            response object is the one defined by the requests library.
            Useful resources in understanding this raw response object:
                https://realpython.com/python-requests/#the-response
                https://requests.kennethreitz.org/en/master/api/#requests.Response
            HINT: raw_response.content gives you the webpage html content.
```
**Return Value**

This function needs to return a list of urls that are scraped from the
response. (An empty list for responses that are empty). These urls will be
added to the Frontier and retrieved from the cache. These urls have to be
filtered so that urls that do not have to be downloaded are not added to the
frontier.

The first step of filtering the urls can be by using the **is_valid** function
provided in the same scraper.py file. Additional rules should be added to the is_valid function to filter the urls.

EXECUTION
-------------------------

To execute the crawler run the launch.py command.
```python3 launch.py```

You can restart the crawler from the seed url
(all current progress will be deleted) using the command
```python3 launch.py --restart```

You can specify a different config file to use by using the command with the option
```python3 launch.py --config_file path/to/config```

THINGS TO KEEP IN MIND
-------------------------

1. It is important to filter out urls that do not point to a webpage. For
   example, PDFs, PPTs, css, js, etc. The is_valid filters a large number of
   such extensions, but there may be more.
2. It is important to filter out urls that are not with ics.uci.edu domain.
3. It is important to maintain the politeness to the cache server (on a per
   domain basis).
4. It is important to set the user agent in the config.ini correctly to get
   credit for hitting the cache servers.
5. Launching multiple instances of the crawler will download the same urls in
   both. Mechanisms can be used to avoid that, however the politeness limits
   still apply and will be checked.
6. Do not attempt to download the links directly from ics servers.
