from services.inventory_parser.inventory_parser_controller import InventoryParserController
from services.seller.seller_controller import SellerController


class MainController:
	def __init__(self):
		self.inventory_parser_controller = InventoryParserController()
		self.inventory_parser_controller.show_seller_view_signal.connect(self.show_seller_view)

	def set_user_data(self, user, session):
		self.user = user
		self.session = session
		
		self.inventory_parser_controller.set_user_data(self.user, self.session)

	def start(self):
		self.inventory_parser_controller.start()

	def show_seller_view(self, data):
		self.sell_controller = SellerController()
		self.sell_controller.set_user_data(self.user, self.session)
		self.sell_controller.start(data)