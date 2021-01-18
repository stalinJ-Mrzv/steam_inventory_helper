class InventoryItem:
	def __init__(self, data):
		self.data = data

	def calc_total_price(self):
		price = self.data.get('price')
		amount = self.data.get('amount')
		if price and amount:
			self.data['total_price'] = float('{:.2f}'.format(float(price) * amount))