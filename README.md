# Process Overview

This tutorial creates an API endpoint and AWS Lambda function. The tutorial uses an Excel VBA Macro to call the endpoint. The Lambda function creates a graph of the supplied JSON data and emails the graph to a recipient.

AWS Lambda receives JSON request and:

	1. Generates chart/graph with mathplotlib
	2. Connects to gmail smtp, sending the file as an attachment

Excel VBA Macro
	
	1. Iterates through rows of a spreadsheet and minimally scrubs data
	2. Constructs a JSON string and calls the API endpoint

# Introduction / Pre-requisites

For starters, you may have heard of a lambda function before. AWS names their service Lambda, which has little correlation to a lambda function. For lambda functions in Python see: https://en.wikipedia.org/wiki/Anonymous_function

For this tutorial you will need an AWS account. Luckily AWS offers a free tier which allows you to make a certain number of requests for free, but you will need your credit card to sign up.

Another pre-requisite for this tutorial is virtualenv (https://virtualenv.pypa.io/en/latest/). There are many uses for virtualenv, reading the introductory 4 paragraphs of the documentation will provide insight into these uses.

Lastly you will need a separate gmail account that you shouldn't rely on as being overly secure. For brevity this tutorial lacks heightened security measures and assumes that the information you are working with is not sensitive to your organization.

You have already seen the design/process that we will be pursuing in the overview section, so let's get started.

# Warnings

This tutorial does not address security between access points. This tutorial does not adequately address security in general.

# Creating a Lambda function / Using Function Designer

* In your AWS Services Dashboard go to Compute -> Lambda

* Select Create a Function

* Choose Author from scratch

* Name your function emailGraph

* Choose Python3.6 for your runtime.

* Select Create a new role from one or more templates.

* Name your role roleEmailGraph

* Choose simple microservice permissions for your policy template

* Choose Create Function

* Add a trigger to your function. A trigger allows the function to be called using HTTP. 

* Choose to add an API Gateway Trigger

* Choose Create a new API

* !! Choose Open with API key

* Click Add

* Now click Save in the top right.

### IMPORTANT !!

Make sure your trigger uses an API Key and that you share this API Key with no one, otherwise malicious users of your API could make repetitive nuisance calls, costing you a significant amount of money.

## Optional security

For added security you can instead read: https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-create-api.html and create an API Gateway with a resource policy definition file. Unfortunately editing the resource policy file having created the Lambda function as described above is not possible as it uses a proxy to prevent certain activity. IE: This tutorial is using a method that is quick for learning and personal purposes (so long as you don't give away your key) but not adequate for deployment purposes. The other process is beyond the scope of this document.

# Seeing that our endpoint works

At this point we should be able to see that our basic API endpoint works.

If you click on the API Gateway box you should see a details summary:

Details
API endpoint: <ENDPOINT>
API key: <API-KEY>
Authorization: NONE
Method: ANY
Resource path: /emailGraph
Stage: default

If you enter the following line into your Linux terminal you should see a Hello from Lambda response

```
curl -X POST -H "x-api-key: <API-KEY-HERE>" -H "Content-Type: application/json" <ENDPOINT HERE>
```

The curl command sends a request of type POST and using header key/values 'x-api-key: <API-KEY>' and 'Content-Type: application/json'

# emailGraph Function code

Because we are using matplotlib we can't use the inline editor and instead need to create a .zip file to upload.

Let's create a virtualenv for ourselves. This virtualenv will mimick the environment on AWS, it will be completely empty.

From Linux console:

```
> py3-virtualenv venv_emailGraph

> source venv_emailGraph/bin/activate
```

Our virtualenv will mimick the virtualenv of AWS and we will use a small helper package to see our script run locally before we deploy it to AWS, so we install python-lambda-local

```
> pip install python-lambda-local
```

Let's install the matplotlib package next. Instead of installing to the venv we will install to a project directory. This can get a little messy.

Create a project directory which will be the zipped directory sent to AWS. Install matplotlib and pandas.

```
mkdir project_emailGraph

pip install matplotlib -t /path/to/project_emailGraph

pip install pandas -t /path/to/project_emailGraph
```

And let's check if everything is working by creating an lambda_function.py file in our project_emailGraph directory containing:

```python
import json
import matplotlib as mp
import matplotlib._version

def lambda_handler(event, context):
    
    # Create a return dict
    rdict = matplotlib._version.get_versions()
    
    # Update the return dict with the hello string
    rdict.update({'greeting':'Hello from Lambda!'})
    
    return {
        'statusCode': 200,
        'body': json.dumps(rdict)
    }

# used by python-lambda-local, calls and returns lambda_handler
def handler(event,context):
    return lambda_handler(event, context)
```

Open an interactive console:

```
>>> import lambda_function # import the py file
>>> lambda_function.lambda_handler(None,None)
{'statusCode': 200, 'body': '{"dirty": false, "error": null, "full-revisionid": "8858a0d1bdd149a0897789e8503ac586be14676d", "version": "3.0.2", "greeting": "Hello from Lambda!"}'}
```

From here we can zip our package and send to AWS. Before zipping we clean the directory of pyc files and remove the __pycache__ directory.

cd project_emailGraph

```
python3 -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
python3 -c "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"
zip -r projectEmailGraph.zip .
```

Upload the zip file and choose save. 

Executing the same curl command:

```
curl -X POST -H "x-api-key: <API-KEY-HERE>" -H "Content-Type: application/json" <ENDPOINT HERE>
```

Should result in:

```
{"dirty": false, "error": null, "full-revisionid": "8858a0d1bdd149a0897789e8503ac586be14676d", "version": "3.0.2", "greeting": "Hello from Lambda!"}
```

This means that we have succesfully added matplotlib to lambda.

If you are having a problem getting to this step I would advise creating a Test function/event with the body of the test being {}, run it and view the log to see what went wrong.

Incase this changes with future versions of Lambda the information is available https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html


# Loading test data

Let's create a test dataset, similar to what we would expect to receive from our Excel document. Create a new test in AWS with the following. ALSO create an event00.json file containing the same in your project directory.

```
{
    "egyptsecurity":
        [
            {
                "id": "201701010024",
                "year": "2017",
                "month": "1",
                "day":"1",
                "city": "Cairo",
                "lat":"30.084629",
                "lng":"31.334314",
                "type":"Bombing/Explosion",
                "target":"Unnamed Civilian/Unspecified"
            },
            {
                "id": "201701030038",
                "year": "2017",
                "month": "1",
                "day":"3",
                "city": "Ibsheway",
                "lat":"29.360998",
                "lng":"30.68244",
                "type":"Armed Assault",
                "target":"Police Patrol (including vehicles and convoys)"
            },
            {
                "id": "201701030050",
                "year": "2017",
                "month": "1",
                "day":"3",
                "city": "Alexandria",
                "lat":"31.200092",
                "lng":"29.918739",
                "type":"Armed Assault",
                "target":"Retail/Grocery/Bakery"
            },

	    {
		"id": "201701060037",
		"year": "2017",
		"month": "1",
		"day":"6",
		"city": "Hasna",
		"lat":"30.4653",
		"lng":"33.785694",
		"type":"Armed Assault",
		"target":"Military Checkpoint"
	    }

        ]
}
```


This dataset comes from Kaggle's Global Terrorism Database: https://www.kaggle.com/START-UMD/gtd/version/3

Now we can use our python-lambda-local from the command line to see the result on our local machine.

> python-lambda-local lambda_function.py event00.json

The RESULT log entry of above command should produce an identical line as the curl result did.

We can see that we have 3 ways of running our function. The first way is with an interactive Python console, sending it None and None as the context and event function arguments. The second way is having python-lambda-local create event and context objects from the event00.json file. Both of these two methods we will consider our development environment. The final way of running our function is after it has been deployed on AWS using curl. This last method is our deploy environment. 

# Adding functionality to lambda_function.py

## Creating a graph

### We will modify our lambda_function to create the most basic graph.

```python

import json
import matplotlib as mp
import matplotlib._version
import pandas as pd
import smtplib # required to send email
from os import environ
from datetime import date, datetime
from io import BytesIO # required for converting matplotlib figure to bytes
from email.mime.image import MIMEImage # required for image attachment
from email.mime.multipart import MIMEMultipart # required for image attachment
from email.mime.text import MIMEText # required for message body

def lambda_handler(event, context):
 
    # used to calculate the number of incidents per day
    day_accumulator = {}

    # because we are using AWS Lambda behind their new? AWS proxy, the
    # event object is different than what is documented. It contains the 
    # request data within event['body', for this reason we need to make sure
    # we are using event consistently in deployment and development
    eventobj = None
    if 'AWSDEPLOY' in environ and environ['AWSDEPLOY'] == 'TRUE':
        try: 
            eventobj = json.loads(event['body'])
        except Exception as e:
            # don't throw an error because AWS Lambda uses the non
            # proxy technique for their tests
            eventobj = event
    else:
        eventobj = event


    # put all of the entries into a dict
    try: 
        if len(eventobj['egyptsecurity']) == 0:
            return failure('Request made with event list size of 0')

        for item in eventobj['egyptsecurity']:
        
            eventdate = date(int(item['year']), 
                             int(item['month']), 
                             int(item['day']))
        
            if eventdate in day_accumulator:
                day_accumulator[eventdate] += 1
            else:
                day_accumulator[eventdate] = 1
    except Exception as e:
        return failure(str(e))

    # make a list out of the keys (dates) for creating indices for the dataframe
    pddates = day_accumulator.keys()

    # make a list out of the values (integer values) for creating the first 
    # column of the dataframe this is list comprehension, more info: 
    # https://www.pythonforbeginners.com/basics/list-comprehensions-in-python
    # we are using it because day_accumulator.values is of type 
    # <class 'dict_values'>, an iterable but not a list
    pdevents = [y for y in day_accumulator.values()] 

    # because we have gaps in dates that we want to fill in we will need the 
    # min and max date from our list of dates
    oldest = min(pddates)
    newest = max(pddates)

    # Finally create our dataframe
    df = pd.DataFrame({'Number of Attacks':pd.Series(pdevents,index=pddates)})

    # Create a daterange for re-indexing
    daterange = pd.date_range(oldest, newest)

    # Re-index our dataframe, filling the columns of newly created rows for 
    # days with no data with values of 0
    df = df.reindex(daterange, fill_value=0)

    # get ready for plotting with matplotlib, because TKinter is not installed 
    # use Agg as a renderedfor more information about renderers: 
    # https://matplotlib.org/faq/usage_faq.html?highlight=backend#what-is-a-backend
    mp.use('Agg')

    # create a line graph
    plot = df.plot.line()

    # create a figure for the line graph 
    fig = plot.get_figure()

```

### We will convert the figure into byte format for writing as an image attachment.

```python

    # create a bytesIO object because we don't have persistent storage on lambda
    figdata = BytesIO()

    # save the figure to the BytesIO object, SVG was having a difficulty so I 
    # chose PNG, I suppose SVG header information is being saved wrong
    fig.savefig(figdata, format='png')

    # after writing the byte stream the seek position will be at the end
    # of the file, seek to position 0 for re-reading
    figdata.seek(0)

```

### We will create the mail message and send it

```python

    # Create a mail msg object
    # for an explanation of 'alternative' please see: 
    # https://en.wikipedia.org/wiki/MIME#Alternative
    msg = MIMEMultipart('alternative')

    msg['Subject'] = 'New report for ' + '%s' % datetime.now()
    
    if 'FROM' not in environ:
        return failure('Misconfigured environment variable FROM')

    msg['From'] = environ['FROM']

    if 'TO' not in environ:
        return failure('Misconfigured environment variable TO')

    msg['To'] = environ['TO']
    
    # Create the body of the message (a plain-text and an HTML version).
    text = "Hi!\nPlease find attached the graph of today's report."
    html = """\
    <html>
        <head></head>
        <body>
            <p>
                Hi!
                <br><br>
                The below graph shows number of attacks per day in Cairo.
                <br><br>
                <img src="cid:image1">
            </p>
        </body>
    </html>
    """

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # figdata.read(-1) reads the bytes of the figures till the end of the file
    img = MIMEImage(figdata.read(-1), _subtype="png")

    # add a header entry for the filename, name it simply report.png
    img.add_header('Content-Disposition', 'attachment; filename="report.png"')
    
    # add a Content-ID tag for embedding the image in the email
    img.add_header('Content-ID', '<image1>')
    
    # finally attach the img to the email message
    msg.attach(img)

    # set up variables for mailing
    username = environ['FROM']
    
    if 'GMAILPASS' not in environ:
        return failure('Misconfigured environment variables')
    
    password = environ['GMAILPASS']
    server = smtplib.SMTP('smtp.gmail.com:587')

    # login and send the mail
    # it would be advisable to check the response, and log the response if it's 
    # a failure, logging is outside the scope of this tutorial
    server.starttls()
    server.login(username,password)
    server.send_message(msg)
    # close the server connection
    server.quit()


```

### We will return success

```python

    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }

```

We will add a failure function to handle bad requests.

```python

# Boy is this job hard! We need some light natured jovial code to lighten our
# path so we'll use status code 418 - 'I'm a teapot' to signify a client error
# The RFC specifies this code should be returned by teapots requested to brew 
# coffee.
def failure(message):
    return {
        'statusCode': 418, # paying attention? change to 400 - Bad Request
        'body': json.dumps(message)
    }
```


### We will modify our AWS setting for longer than 3 seconds.

Because this function requires longer than 3 second to execute I change execution time on AWS to 1 minute. This is found under Basic Settings under the location you upload your zip file.


# Setting up environment variables

On Linux, to set an environment variable:

```
export GMAILPASS=<YOUR-PASSWORD-HERE>
export AWSDEPLOY=FALSE
export FROM=<FROM-EMAIL-ADDRESS>
export TO=<TO-EMAIL-ADDRESS>
```

To check that it was set:

```
env | grep GMAILPASS
env | grep AWSDEPLOY
env | grep FROM
env | grep TO
```

On Windows, to set an environment variable:

TODO

On Mac, to set an environment variable:

TODO

Next, we also need to set the environment variable for AWS, our deploy environment.

Scroll down to the section titled Environment variables:

key: GMAILPASS and for Value use the password
key: AWSDEPLOY and for Value use TRUE
key: FROM ...
key: TO ...

For added security you can encrypt your password but that is beyond the scope of this tutorial.
 

### Checking that our function works

You can check that this newly created function works by:

curl -X POST -H "x-api-key: <YOUR-API-KEY-HERE>" -H "Content-Type: application/json" -d '{"egyptsecurity":[{"id":"201701010024","year":"2017","month":"1","day":"1","city":"Cairo","lat":"30.084629","lng":"31.334314","type":"Bombing/Explosion","target":"UnnamedCivilian/Unspecified"},{"id":"201701030038","year":"2017","month":"1","day":"3","city":"Ibsheway","lat":"29.360998","lng":"30.68244","type":"ArmedAssault","target":"PolicePatrol(includingvehiclesandconvoys)"},{"id":"201701030050","year":"2017","month":"1","day":"3","city":"Alexandria","lat":"31.200092","lng":"29.918739","type":"ArmedAssault","target":"Retail/Grocery/Bakery"},{"id":"201701060037","year":"2017","month":"1","day":"6","city":"Hasna","lat":"30.4653","lng":"33.785694","type":"ArmedAssault","target":"MilitaryCheckpoint"}]}' <YOUR-API-URL-ENDPOINT-HERE>


# VBA Part

I created the macro with the following VBA code:

```vbnet
Sub MakeAPICall()
    Rem Taken directly from the Microsoft VBA documentation, these next 3 lines
    Rem find the last row and last column of the spreadsheet
    Dim LastRow As Long, LastColumn As Long
    LastRow = Cells.Find(What:="*", After:=Range("A1"), SearchOrder:=xlByRows, SearchDirection:=xlPrevious).Row
    LastColumn = Cells.Find(What:="*", After:=Range("A1"), SearchOrder:=xlByColumns, SearchDirection:=xlPrevious).Column
    
    Rem Because this is overly simplified we really only need year month and day
    Dim year As Variant
    Dim month As Variant
    Dim day As Variant
    
    Rem I looked for a nicer loads/dumps json equivalent but was unable to
    Rem find one that could handle nested dictionaries and lists, so i resorted
    Rem to using a simple string, here we are constructing a json string
    Dim datastring As String
    datastring = "{""egyptsecurity"":["
    
    Rem The integer c is incremented each iteration of the loop, allowing
    Rem us to insert a comma after each dictionary in the list
    Dim c As Integer
    c = 0
    
    Rem iterate through the rows of the spreadsheet, starting at row 2
    Rem the first row is a header row
    For Each rw In Range("A2").Resize(LastRow, LastColumn).Rows
        
        Rem assign year,month and day
        year = rw.Cells(2).Value
        month = rw.Cells(3).Value
        day = rw.Cells(4).Value
        
        Rem possibly unnecessay, check to make sure that year, month and day
        Rem are not empty
        If CStr(year) <> "" And CStr(month) <> "" And CStr(day) <> "" Then
            
            Rem I found two entries in the excel spreadsheet with 0 as they day
            Rem so I took liberty in changing these to 1
            If CStr(day) = "0" Then
                day = "1"
            End If
                
            Rem if we are not at the first dict entry then add a comma
            If c <> 0 Then
                datastring = datastring + ","
            Else
                Rem if we are at first iteration, increment our iteration count
                c = c + 1
            End If
            
            Rem construct another dict entry for our json string
            datastring = datastring + "{""year"":" + Chr(34)
            datastring = datastring + CStr(year) + Chr(34)
            datastring = datastring + ",""month"":" + Chr(34)
            datastring = datastring + CStr(month) + Chr(34)
            datastring = datastring + ",""day"":" + Chr(34)
            datastring = datastring + CStr(day) + Chr(34) + "}"
        
        End If
        
    Next rw
    
    Rem after iterating the spreadsheet finish off our json string
    datastring = datastring + "]}"
    
    Rem create an HTTP object for making the request
    Set objHTTP = CreateObject("MSXML2.ServerXMLHTTP")
    
    Rem set the url
    Url = "YOUR-ENDPOINT-URL-HERE"
    
    Rem initialize the object, setting the request type and setting it to be
    Rem synchronous, we'll have to wait for aws lambda to return a response
    objHTTP.Open "POST", Url, False
    
    Rem set the api-key header
    objHTTP.setRequestHeader "x-api-key", "YOUR-API-KEY-HERE"
    
    Rem set the content-type header
    objHTTP.setRequestHeader "Content-Type", "application/json"
    
    Rem finally make the request, send the datastring that we constructed
    objHTTP.send datastring
    
    Rem create a simple msgbox with the contents of the response
    MsgBox objHTTP.responseText
    
End Sub
```


Running this macro results in getting this chart in our inbox.

![alt text](https://github.com/btardio/atad_awsLambda/blob/master/report.png "Chart")


# Mistakes / Improvements

The biggest glaring mistake is the use of 'egyptsecurity'. A better naming convention would have been to use 'records' or 'entries.'

There's a possibility that in my haste the Excel document contains values in cells that I missed wrangling in the VBA code. For example, besides having the values of 0 for the day column, some cells may have more days than are allowed in a certain month.

In hindsight I would have liked to include a TO field in the AWS Lambda function that allows the recipient to be specified in the JSON. 



# Don't Forget

Don't forget to change the alloted resources for the function, including execution time and memory allotment.

# Conclusion

AWS Lambda provides us with a platform for deploying an API endpoint that can become another part of our data analysis pipeline. It is convenient to us because the uptime of the service is near 99.9%. It is not convenient, yet, as being something multiple people can use, that may require us to improve authentication method and read further about the API Gateway because we are currently using a managed proxied version of AWS Lambda. I hope you can also see the benefits of AWS Lambda and will consider using it to fill in missing pieces in your data analysis pipeline or adding functionality to your data analysis tasks.

Please feel free to email me with any questions.






