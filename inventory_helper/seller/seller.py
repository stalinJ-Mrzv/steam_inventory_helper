import requests

import steam.webauth as wa


class Seller:
	def __init__(self, user, session):
		self.user = user
		self.session = session

	def set_user_info(self, user, session):
		self.user = user
		self.session = session

	def sell(self, app_id, context_id, asset_id, amount, price):
		is_send_sell_request = False
		message = 'OK'

		if self.session:
			data, headers = self.__get_basic_data()

			self.session.headers = headers
			try:
				response = session.post('https://steamcommunity.com/market/sellitem/', data=data)
				json_response = response.json()
				is_send_sell_request = json_response.get('success')
				if not is_send_sell_request:
					message = json_response.get('message')

			except ValueError as e:
				message = str(e)
		else:
			message = 'session is none'

		return is_send_sell_request, message

	def __get_basic_data(self):
		data = {
			'sessionid': self.user.session_id,
			'appid': app_id,
			'contextid': context_id,
			'assetid': asset_id,
			'amount': amount,
			'price': price
		}

		headers = {
			'Origin': 'https://steamcommunity.com',
			'Host': 'steamcommunity.com',
			'Referer': 'https://steamcommunity.com/profiles/' + str(self.user.steam_id.as_64) + '/inventory/',
			'Connection': 'keep-alive'
		}

		return data, headers
			

