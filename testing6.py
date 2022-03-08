# importing the requests library
import requests
  
# api-endpoint
URL = "https://api.zapper.fi/v1/balances?addresses%5B%5D=0xa44b23b95eb449e69dc84a644f3d0a8f2321a8ad&api_key=96e0cc51-a62e-42ca-acee-910ea7d2a241"
URL = "https://api.zapper.fi/v1/balances?addresses%5B%5D=0xa44b23b95eb449e69dc84a644f3d0a8f2321a8ad&api_key=96e0cc51-a62e-42ca-acee-910ea7d2a241"  
# location given here
location = "delhi technological university"
  
# defining a params dict for the parameters to be sent to the API
PARAMS = {'address':location}
  
# sending get request and saving the response as response object
r = requests.get(url = URL)
  
# extracting data in json format
#data = r.json()
print(r)