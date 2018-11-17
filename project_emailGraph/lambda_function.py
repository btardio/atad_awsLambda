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

# Boy is this job hard! We need some light natured jovial code to lighten our
# path so we'll use status code 418 - 'I'm a teapot' to signify a client error
# The RFC specifies this code should be returned by teapots requested to brew 
# coffee.
def failure(message):
    return {
        'statusCode': 418, # paying attention? change to 400 - Bad Request
        'body': json.dumps(message)
    }


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

    # create a bytesIO object because we don't have persistent storage on lambda
    figdata = BytesIO()

    # save the figure to the BytesIO object, SVG was having a difficulty so I 
    # chose PNG, I suppose SVG header information is being saved wrong
    fig.savefig(figdata, format='png')

    # after writing the byte stream the seek position will be at the end
    # of the file, seek to position 0 for re-reading
    figdata.seek(0)

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

    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }

def handler(event,context):
    return lambda_handler(event, context)


