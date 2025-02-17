import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, api_key, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        if api_key:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                        params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                        params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs): 
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        print("Network exception occurred")
        return "error in post request"

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, None)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["dealerships"]
        # For each dealer object
        for dealer in dealers:
            # Create a CarDealer object with values in `doc` object
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
def get_dealer_reviews_from_cf(url, dealerId, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, None, dealerId=dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        dealer_reviews = json_result["reviews"]
        # For each dealer object
        for dealer_review in dealer_reviews:
            # Create a CarDealer object with values in `doc` object
            dealer_review_obj = DealerReview(
                dealer_review["dealership"],
                dealer_review["name"],
                dealer_review["purchase"],
                dealer_review["review"],
                dealer_review["purchase_date"],
                dealer_review["car_make"],
                dealer_review["car_model"],
                dealer_review["car_year"],
                analyze_review_sentiments(dealer_review["review"], version = "2022-04-07", features ="sentiment", return_analyzed_text=True),
                dealer_review["id"])

            results.append(dealer_review_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview, **kwargs):
    params = dict()
    params["text"] = dealerreview
    params["version"] = kwargs["version"]
    params["features"] = kwargs["features"]
    params["return_analyzed_text"] = kwargs["return_analyzed_text"]
    params["language"] = "en"
    
    try:
        response = get_request("https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/152f52a8-88c2-4427-861a-4317f0011238", 'yfOsuwFVXLpNfuTeAIzsjSG81fsgC_wCanV8Ro-N6JC7')
        return json.loads(response.text)['sentiment']['document']['label'] 
    except:
        print("Network exception occurred")
        return "error in sentiment analyze"

