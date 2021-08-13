import requests
import json
from .models import CarDealer
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))

def get_request(url, **kwargs):
    """
    Utility function to make HTTP GET requests
    """
    print("\nGET from {} with paramaters {}".format(url,kwargs))
    try:
        if 'apikey' in kwargs:
            # ...separate apikey from kwargs to submit separately
            api_key = kwargs.pop('apikey')
            # ...verify we just have the parameters now
            print("Updated parameters: {}".format(kwargs))
            # ...call the get method in request lib
            response = requests.get(url, headers={'Content-type': 'application/json'}, 
                params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            # ...calling the request lib's get method with URL + params and store it
            response = requests.get(url, headers={'Content-type': 'application/json'},
                params=kwargs)
                # params = kwargs? //I mean i guess it's working.
    except:
        # ...if that fails leave a general note.
        print("Network exception occurred")
    # relay status code info to console
    status_code = response.status_code
    print("Response Final URL {}".format(response.url))
    print("Response status {} \n".format(status_code))
    # package and return json data
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    """
    Utility function to make HTTP POST requests
    """
    print("POST to {} with paramaters {} \nIncludes payload: {}".format(url,kwargs, json_payload))
    try:
        # ...calling url with POST method from requests lib with payload
        response = requests.post(url, headers={'Content-type': 'application/json'}, 
            json=json_payload) # don't wanna include params, just the json.
    except:
        print("Network exception occurred.")
    
    # relay status code info to console and caller
    status_code = response.status_code
    print("Response Final URL {}".format(response.url))
    print("Response status {} \n".format(status_code))
    return status_code

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    else:
        results = 'Could not pull dealers from database: ' + json_result.get('error', 'no error message provided.')

    return results

def get_dealer_by_state_from_cf(url, **kwargs):
    """
    This function calls get_request() w/ the specified args (state) then:
        1. Parses the json data returned from the request / "get-state-dealers" Cloud function
        2. Puts it into a proxy CarDealer obj
        3. Creates and returns a list of those proxies.
    """
    results = []
    # Check for "required" kwargs then make request
    if 'state' in kwargs:
        json_result = get_request(url, state=kwargs.get('state'))
    else:
        print('State (Abbrev.) not supplied in kwargs.')
        results.append('Could not execute request: missing state abbreviation')
    
    # Continue with business
    if 'entries' in json_result:
        dealers = json_result.get('entries','Could not pull entries.')

        for dealer in dealers:
            # Reincarnate each JSON obj as a CarDealerObj
            dealer_obj = CarDealer(dealer)
            #verify new obj
            print(dealer_obj.full_name)
            results.append(dealer_obj)
    else:
        print('No entries received for State {}'.format(kwargs.get('state','N/A')))
        results = 'Could not retrieve Dealer data for the given state.'
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    """
    This function calls get_request() w/ the specified args (dealerId) then:
        1. Parses the json data returned from the request / "get-dealer-reviews" Cloud function
        2. Puts it into a proxy DealerReviews obj.
        3. Creates and returns a list of those proxies.
    
    For some reason, this requires authentication be sent with the request... but is a public api.
    """
    results =[]

    # Check for "required" kwargs then make request
    if 'dealerId' in kwargs:
        json_result = get_request(url, dealerId=kwargs['dealerId'])
    else:
        print('Dealer ID not supplied in kwargs.')
        results.append("Could not execute request: missing Dealer ID")
    
    # Continue with business
    if 'entries' in json_result:
        reviews = json_result.get('entries')

        for review in reviews:
            # take each review and pass the dict/JSON obj to the Dealer Review constructor
            review_obj = DealerReview(review)
            # verify new obj - this stuff should be going to the logger...
            #print(review_obj.review)
            # Analyze the review sentiment + set it as the property
            nlu_result = analyze_review_sentiments(review_obj.review)
            sentiment = ""
            if 'sentiment' in nlu_result:
                sentiment = nlu_result['sentiment']['document']['label']
            elif 'error' in nlu_result:
                sentiment = 'unknown ' + nlu_result.get('error')
            review_obj.sentiment = sentiment
            print("Review ID{} sentiment rating: {}".format(review_obj.id, review_obj.sentiment))
            results.append(review_obj)

    else:
        print('No entries received for Dealer Id {}'.format(kwargs.get('dealerId')))
        results = 'Could not retrieve review data: ' + json.get('error')
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative



