import requests

import steam.webauth as wa


class Seller:
	def __init__(self, user, session):
		self.user = user
		self.session = session

	def set_user_info(self, user, session):
		self.user = user
		self.session = session

	def sell(self, sell_item):
		is_send_sell_request = False
		message = 'OK'

		if self.session:
			data, headers = self.__get_basic_data(sell_item)

			self.session.headers = headers
			try:
				response = self.session.post('https://steamcommunity.com/market/sellitem/', data=data)
				json_response = response.json()
				is_send_sell_request = json_response.get('success')
				if not is_send_sell_request:
					message = json_response.get('message')

			except ValueError as e:
				message = str(e)
		else:
			message = 'session is none'

		return is_send_sell_request, message

	def __get_basic_data(self, sell_item):
		item_data = sell_item.get_data()

		data = {
			'sessionid': self.user.session_id,
			'appid': item_data.get('app_id'),
			'contextid': item_data.get('context_id'),
			'assetid': item_data.get('asset_id'),
			'amount': 1,
			'price': item_data.get('price')
		}

		headers = {
			'Origin': 'https://steamcommunity.com',
			'Host': 'steamcommunity.com',
			'Referer': 'https://steamcommunity.com/profiles/' + str(self.user.steam_id.as_64) + '/inventory/',
			'Connection': 'keep-alive'
		}

		return data, headers
			

