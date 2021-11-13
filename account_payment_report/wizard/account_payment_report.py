from odoo import fields, models, api, _
from odoo.tools.misc import get_lang

import logging
_logger = logging.getLogger(__name__)
class AccountPaymentReport(models.TransientModel):
	_name = "account.payment.report"
	_description = "Report payment"

	user_id = fields.Many2one('res.users', string="User", required=True, default=lambda self: self.env.user)
	date_from = fields.Date(string="Date From", required=True, default=fields.Date.context_today)
	date_to = fields.Date(string="Date To", required=True,default=fields.Date.context_today)
	company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)

	def _build_contexts(self, data):
		result = {}
		result['date_from'] = data['form']['date_from'] or False
		result['date_to'] = data['form']['date_to'] or False
		result['user_id'] = data['form']['user_id'][0] or False
		result['company_id'] = data['form']['company_id'][0] or False
		return result

	def _print_report(self, data):
		return self.env.ref('account_payment_report.account_payment_cash_report').report_action(self, data=data)

	def check_report(self):
		self.ensure_one()
		data = {}
		data['ids'] = self.env.context.get('active_ids', [])
		data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(['date_from', 'date_to', 'user_id', 'company_id'])[0]
		used_context = self._build_contexts(data)
		data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
		return self.with_context(discard_logo_check=True)._print_report(data)