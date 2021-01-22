class SellItem:
	'''
		data:
		app_id
		context_id
		asset_id
		market_hash_name
		price
	'''

	def __init__(self, data):
		self.__data = data

	def set_data(self, data):
		self.__data = data

	def get_data(self):
		return self.__data