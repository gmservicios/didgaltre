from odoo import models, fields, api, _

class SaleOrder(models.Model):
	_inherit = "sale.order"

	def action_confirm(self):
		res = super(SaleOrder,self).action_confirm()
		for order in self:
			for picking in order.picking_ids:
				picking.action_assign()
				picking.action_confirm()
				for mv in picking.move_ids_without_package:
					mv.quantity_done = mv.product_uom_qty
				for mv in picking.move_line_ids_without_package:
					mv.product_uom_qty = mv.qty_done
				picking.action_assign()
				# picking.button_validate()
		return res

	def action_create_invoice(self):
		for order in self.filtered(lambda o: o.state == 'sale'):
			order._create_invoices()
