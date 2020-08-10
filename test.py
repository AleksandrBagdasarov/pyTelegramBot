import requests


token = '1070073381:AAE1Hu8uysrlKkYhvY3QdkIS6Gh4miU343I'
method_name = r'deleteMessage'
payload = {'chat_id': 326793331, 'message_id': 4586}

request_url = f"https://api.telegram.org/bot{token}/{method_name}"

requests.post(request_url, data=payload)