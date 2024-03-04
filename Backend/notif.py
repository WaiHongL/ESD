from mailjet_rest import Client
import os
api_key = 'd2d21f40f8f6cd7b51784638c46b078b'
api_secret = '7c5652e91572a9fb541b985737e0371a'
mailjet = Client(auth=(api_key, api_secret))
id = '576460774925514646'
result = mailjet.message.get(id=id)
print (result.status_code)
print (result.json())