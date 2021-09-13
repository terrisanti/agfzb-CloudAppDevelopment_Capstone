import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))

def get_request(url, **kwargs):  
    #print(kwargs)
    #print("GET from {} ".format(url))  
    try:
        if "apikey" in kwargs:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', kwargs["apikey"]))
            status_code = response.status_code
            json_data = json.loads(response.content)
            return json_data
        else:
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
            status_code = response.status_code
            json_data = json.loads(response.text)
            return json_data
    except:
        # If any error occurs
        print("Network exception occurred")


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    """
    Utility function to make HTTP POST requests
    """
    # print("POST to {} with paramaters {} \nIncludes payload: {}".format(url,kwargs, json_payload))
    try:
        response = requests.post(url, headers={'Content-type': 'application/json'}, 
            json=json_payload)
    except:
        print("Network exception occurred.")
    
    # status_code = response.status_code
    return response

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
        dealers = json_result["entries"]
        # For each dealer object
        for dealer in dealers:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)
    else:
        results = 'Could not pull dealers from database: ' + json_result.get('error', 'no error message provided.')

    return results

def get_dealer_by_state_from_cf(url, state): 

    results = []
    # - Call get_request() with specified arguments
    json_result = get_request(url, state=state)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["entries"]
        # For each dealer object
        for dealer in dealers:
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealer_id):

    results = []
    # - Call get_request() with specified arguments
    json_result = get_request(url, dealerId=dealer_id)
    if json_result:
        # Get the row list in JSON as reviews
        reviews_list = json_result["entries"]
        # For each review object
        for review in reviews_list:
            review_obj = DealerReview(id=review["id"], name=review.get("name",""), dealership=review["dealership"], review=review["review"],
                                   purchase=review.get("purchase","NA"), car_make=review.get("car_make","NA"), car_model=review.get("car_model","NA"),
                                   car_year=review.get("car_year","NA"), purchase_date=review.get("purchase_date","NA"), sentiment=" ")
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            results.append(review_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    doc =  {}
    sentiment = {}
    features = {}
    # - Call get_request() with specified arguments
    apikey = 'VDSAC9J4opOC5eWl0JFqNivPDKrD1HssJQRQDcQzumIF'
    apiurl = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/d7fbf8cd-bf58-4afc-8bc1-27b7fc9d0c04/v1/analyze?version=2019-07-12'
    targets = ["Good","Bad","Great","Excellent", "Unsatisfactory"]
    sentiment["targets"] = targets
    features["sentiment"] = sentiment 
    
    response = get_request(apiurl, text=text, version='2021-08-01',
        features=features, apikey=apikey)
    # - Get the returned sentiment label such as Positive or Negative

    if response:
        senti = response["sentiment"]
        doc = senti["document"]
        return doc["label"]


