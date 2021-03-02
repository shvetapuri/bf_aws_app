# --------------- Helpers that build all of the responses ----------------------
import boto3

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
    	'version': '1.0',
    	'sessionAttributes': session_attributes,
    	'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
	""" If we wanted to initialize the session to have some attributes we could
		add those here
	"""
	session_attributes = {}
	card_title = "Welcome"
	speech_output = "Welcome to the Alexa Breastfeeding skill. " \
	                    "To record feed information say, store feed information. " \
	                    "To get information about your last feed say, when was the last feed "
	# If the user either does not reply to the welcome message or says something
	# that is not understood, they will be prompted again with this text.
	reprompt_text = "Please say store feed, " \
	                    "or get feed."
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
	        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
	card_title = "Session Ended"
	speech_output = "Thank you for using the breastfeeding app. " \
	                    "Have a nice day! "
	 # Setting this to true ends the session and exits the skill.
	should_end_session = True
	return build_response({}, build_speechlet_response(
	        card_title, speech_output, None, should_end_session))


  #  def create_favorite_color_attributes(favorite_color):
   #     return {"favoriteColor": favorite_color}


def set_feedInfo(intent, session):
	""" Sets the feed info in dynamodb
	"""
	card_title = intent['name']
	session_attributes = {}
	reprompt_text = None

	dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
	table = dynamodb.Table('breastfeedinfo')
	nameId = session['user']['userId']

	should_end_session = False

	#from datetime import datetime
	#timeNow=str(datetime.now().strftime("%A %B %d at %I %M %p"))
	
	if len(intent['slots']['startDay']['value']) > 0:
		startDay=intent['slots']['startDay']['value']
		if len(intent['slots']['startTime']['value']) > 0:
			startTime=intent['slots']['startTime']['value']
			if 'value' in intent['slots']['breastOne'].keys():
				whichBreastFed = intent['slots']['breastOne']['value']
				#session_attributes = create_favorite_color_attributes(favorite_color)
				# store whichBreast in dynamodb 
				if 'howLongOne' in intent['slots']:
					howLongFed = intent['slots']['howLongOne']['value']
			
					table.put_item(
						Item= {
							'nameId':nameId,
							'startDay':startDay,
							'startFeedTime': startTime,
							'breastOne': whichBreastFed,
							'howLongOne': howLongFed
						}
						)
					speech_output = "Storing feed started " + startDay + " at " + startTime + " from the " + \
							whichBreastFed + \
	                        " breast for " + howLongFed + " minutes"
				else: 
					speech_output = "I'm not sure how long you fed " \
	                        "Please say the number of minutes fed."
					reprompt_text = "I'm not sure how many minutes you fed " \
	                        "please state the number of minutes fed." 
		
				if 'value' in intent['slots']['breastTwo'].keys():
					whichBreastFedTwo=intent['slots']['breastTwo']['value']
			
					table.update_item (
								Key= {
						       'nameId':nameId,
								},
							UpdateExpression='SET breastTwo = :val1',
							ExpressionAttributeValues={
							':val1': whichBreastFedTwo
							}
							)

					if 'value' in intent['slots']['howLongTwo'].keys():
						howLongFedTwo=intent['slots']['howLongTwo']['value']
				
						table.update_item (
								Key= {
						        'nameId':nameId,
								},
							UpdateExpression='SET howLongTwo = :val1',
							ExpressionAttributeValues={
							':val1': howLongFedTwo
							}
							)
						speech_output = speech_output + " and " + \
									whichBreastFedTwo + \
	                		       " breast for " + howLongFedTwo + " minutes"

					else :
						speech_output = "I'm not sure how long you fed " \
	                        "Please say the number of minutes fed."
						reprompt_text = "I'm not sure how many minutes you fed " \
	                        "please state the number of minutes fed." 
		
			else:
				speech_output = "I'm not sure which breast you fed from" \
	                        "Please say right or left."
				reprompt_text = "I'm not sure which breast you fed from " \
	                        "please say right or left." 
		else: 
			speech_output = "Please specify what time you started feeding."
			reprompt_text = "Please specify what time you started feeding." 

	else:
		speech_output = "Please specify which day you fed on, say today or yesterday."
		reprompt_text = "Please specify which day you fed on, say today or yesterday." 

	                        

	return build_response(session_attributes, build_speechlet_response(
	        card_title, speech_output, reprompt_text, should_end_session))

def get_feedInfo(intent, session):
	session_attributes = {}
	reprompt_text = None
	dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
	table = dynamodb.Table('breastfeedinfo')
	nameId = session['user']['userId']
	#response = table.scan()
	response= table.get_item(Key={'nameId':nameId})
	item=response['Item']
	breastOne=None
	howLongOne=None
	dateTimeString=None
	startDay = None
	startTime = None
	
	if len(str(item['breastOne'])):
		breastOne=str(item['breastOne'])
	if 'howLongOne' in response['Item']:
		howLongOne=str(item['howLongOne'])
	if 'startDay' in response['Item']:
		startDay=str(item['startDay'])
	if 'startFeedTime' in response['Item']:
		startTime = str(item['startFeedTime'])
	
	breastTwo=None	
	howLongTwo=None
	if len(str(item['breastTwo'])) > 0:
		breastTwo=str(item['breastTwo'])
	if len(str(item['howLongTwo']))>0:
		howLongTwo=str(item['howLongTwo'])
		
	if startDay and startTime:
		if breastOne and howLongOne:
			speech_output = "You last fed " + startDay + " at " + startTime + " from the " + breastOne + \
	                        " breast for "+ howLongOne +" minutes"
			if breastTwo and howLongTwo:
				speech_output= speech_output + " and the " + breastTwo + \
						   " breast for " + howLongTwo +" minutes."
			should_end_session = True

		else:
		  speech_output = "Last feed information was not found " \
		                      "to store feed information say store info for then"\
		                      " indicate which breast, and then say how many minutes."
		  should_end_session = False
	else:
		speech_output = "Last feed information was not found " \
		                      "To store feed information say store info for then "\
		                      " indicate which breast, and then say how many minutes."
		should_end_session = False

	# Setting reprompt_text to None signifies that we do not want to reprompt
	# the user. If the user does not respond or says something that is not
	# understood, the session will end.
	return build_response(session_attributes, build_speechlet_response(
	        intent['name'], speech_output, reprompt_text, should_end_session))

def startTiming(intent,session):
	session_attributes = {}
	reprompt_text = None
	dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
	table = dynamodb.Table('breastfeedinfo')
	nameId = session['user']['userId']

	if 'whichBreast' in intent['slots']:
		whichBreastFed = intent['slots']['whichBreast']['value']
		if 'attributes' in session.keys():
			if 'timer' not in session['attributes'].keys():
				session_attributes = {"timer": "started"}
			
				from datetime import datetime
				timeNow=str(datetime.now())
				dateTimeString=str(datetime.now().strftime("%A %B %d at %I %M %p"))

				table.put_item(
					Item={
						'nameId': nameId,
						'timerStartTime':timeNow,
						'dateTimeString' :dateTimeString,
						'whichBreast': whichBreastFed,
						'breastOne': {},
						'howLongOne': {},
						'breastTwo':{},
						'howLongTwo': {}
					}
					)
				speech_output = "Starting breastfeeding timer for " + whichBreastFed +" breast"
			elif session['attributes']['timer']=='started': 
				session_attributes = {"timer": "restarted"}
				#one breast has already been timed, start next breast
				from datetime import datetime
				timeNow=str(datetime.now())
				#dateTimeString=str(datetime.now().strftime("%A %B %d at %I %M %p"))
				
				table.update_item (
					Key= {
					'nameId':nameId,
					},
					UpdateExpression='set whichBreast = :val1, timerStartTime=:val2',
					ExpressionAttributeValues={
						':val1': whichBreastFed,
						':val2': timeNow,
					}
					)
				speech_output = "Starting second breastfeeding timer for " + whichBreastFed +" breast"

			else:
				del session['attributes']["timer"]
				speech_output = "Feed already recorded for both breasts. To get information for this feed say"\
								" get last feed info, or record a new feed by saying set feed info."
				should_end_session = True
				
		should_end_session = False
	else:
		speech_output = "Please specify which breast the timer is for " \
	                        "say right breast or left breast."
		reprompt_text = "Please specify which breast the timer is for " \
	                        "say right breast or left breast."
		should_end_session = False

	return build_response(session_attributes, build_speechlet_response(
	        intent['name'], speech_output, reprompt_text, should_end_session))

def stopTiming(intent, session):
	session_attributes = {}
	should_end_session = False
	reprompt_text = None
	dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
	table = dynamodb.Table('breastfeedinfo')
	nameId = session['user']['userId']
	
	from datetime import datetime
	
	response= table.get_item(Key={
			'nameId':nameId
		}
		)
	startTime=response['Item']['timerStartTime']
	whichBreast=response['Item']['whichBreast']
	dateTimeString = response['Item']['dateTimeString']

	#breastOne = response['Item']['breastOne']
	#speech_output = ""
	if startTime:
		timerDateTime=datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S.%f")
		duration=datetime.now()-timerDateTime
		minutesLasting = str((duration.seconds//60)%60)
		if 'timer' in session['attributes'].keys():
			if session['attributes']['timer']=='started':
				table.update_item (
				Key= {
						'nameId':nameId,
					},
					UpdateExpression='set howLongOne = :val1, breastOne=:val2',
					ExpressionAttributeValues={
						':val1': minutesLasting,
						':val2': whichBreast
					}
					)
				session_attributes = {"timer": "started"}
				should_end_session = False
				speech_output = "Breastfeeding timer stopped, you fed on " + dateTimeString + \
		                 " from the " + whichBreast + " for " \
						+ str(minutesLasting) + " minutes."\
						" If you would like to time a feed from the other breast, please say "\
						"time feed from and which breast."
			elif session['attributes']['timer']=='restarted':
				del session['attributes']['timer']
				table.update_item (
				Key= {
					'nameId':nameId,
					},
					UpdateExpression='set howLongTwo = :val1, breastTwo=:val2',
					ExpressionAttributeValues={
						':val1': minutesLasting,
						':val2': whichBreast
					}
					)
				speech_output = "Breastfeeding timer stopped, you fed on " + dateTimeString + \
		                 "from the " + whichBreast + " for " \
						+ str(minutesLasting) + " minutes."\
						"Your feed session will now end. Say get feed to get last feed information"
				should_end_session = True
			else:
				speech_output= "No start time found, pleast restart timer by saying start timer"
		else:
			speech_output= "No start time found, pleast restart timer by saying start timer"
			#response['breastOne']=whichBreast
			#response['howLongOne']=howLongTwo
			#response.save()
	else:
		speech_output = "No start time found, pleast restart timer by saying start timer"
		
	return build_response(session_attributes, build_speechlet_response(
	        intent['name'], speech_output, reprompt_text, should_end_session))

	# --------------- Events ------------------

def on_session_started(session_started_request, session):
	""" Called when the session starts """
	print("on_session_started requestId=" + session_started_request['requestId']
			+ ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
	""" Called when the user launches the skill without specifying what they
	    want
	"""
	print("on_launch requestId=" + launch_request['requestId'] +
			", sessionId=" + session['sessionId'])
	# Dispatch to your skill's launch
	return get_welcome_response()


def on_intent(intent_request, session):
	""" Called when the user specifies an intent for this skill """

	print("on_intent requestId=" + intent_request['requestId'] +
		", sessionId=" + session['sessionId'])

	intent = intent_request['intent']
	intent_name = intent_request['intent']['name']

	    # Dispatch to your skill's intent handlers
	if intent_name == "GetLastFeedInfo":
		return get_feedInfo(intent, session)
	elif intent_name == "StoreLastFeedInfo":
	    return set_feedInfo(intent, session)
	elif intent_name == "StartTiming":
		return startTiming(intent,session)
	elif intent_name == "StopTiming":
		return stopTiming(intent,session)
	elif intent_name == "AMAZON.HelpIntent":
	    return get_welcome_response()
	elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
		return handle_session_end_request()
	else:
	    raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
	""" Called when the user ends the session.
		Is not called when the skill returns should_end_session=true
	"""
	print("on_session_ended requestId=" + session_ended_request['requestId'] +
	          ", sessionId=" + session['sessionId'])
	    # add cleanup logic here


	# --------------- Main handler ------------------

def lambda_handler(event, context):
	""" Route the incoming request based on type (LaunchRequest, IntentRequest,
		etc.) The JSON body of the request is provided in the event parameter.
	"""
	print("event.session.application.applicationId=" +
	          event['session']['application']['applicationId'])

	"""
	    Uncomment this if statement and populate with your skill's application ID to
	    prevent someone else from configuring a skill that sends requests to this
	    function.
	"""
	if (event['session']['application']['applicationId'] !=
	    "amzn1.ask.skill.4846a404-b961-47d7-9de3-7a24afa415c4"):
		raise ValueError("Invalid Application ID")

	if event['session']['new']:
	        on_session_started({'requestId': event['request']['requestId']},
	                           event['session'])

	if event['request']['type'] == "LaunchRequest":
		return on_launch(event['request'], event['session'])
	elif event['request']['type'] == "IntentRequest":
		return on_intent(event['request'], event['session'])
	elif event['request']['type'] == "SessionEndedRequest":
		return on_session_ended(event['request'], event['session'])
