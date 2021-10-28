from odoo import models, fields, api, _

class PaymentTerm(models.Model):
	_inherit = 'account.payment.term'

	payment_method = fields.Selection(selection=[('counted','Counted'),('credit','Credit')], string="Method payment", required=True)