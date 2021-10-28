from odoo import models, api, fields, _
from odoo.exceptions import UserError

class Partner(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'

	check_credit = fields.Boolean(string="Check credit", default=False)

	def _check_credit_debit_limit(self, amount, date, type):
		credit_doc, debit_doc = self._get_document_credits(date)
		if type == 'receivable':
			if (amount + self.credit) > self.credit_limit:
				raise UserError(_("Your credit limit exceeded\nCredit limit %s\nCredit available %s\nCredit exceeded %s" % (self.credit_limit, self.credit_limit- self.credit, amount - self.credit_limit)))
			if credit_doc:
				raise UserError(_("You have overdue documents\n%s" %("".credit_doc.join())))
		if type == 'payable':
			if (amount + self.debit) > self.debit_limit:
				raise UserError(_("Your credit limit exceeded\nCredit limit %s\nCredit exceeded %s" % (self.debit_limit, amount - self.debit_limit)))
			if debit_doc:
				raise UserError(_("You have overdue documents\n%s" %("\n".debit_doc.join())))

	def _get_document_credits(self, date):
		tables, where_clause, where_params = self.env['account.move.line'].with_context(
			state='posted', company_id=self.env.company.id, aged_balance=True, date_to=date)._query_get()
		where_params = [tuple(self.ids)] + where_params
		if where_clause:
			where_clause = 'AND ' + where_clause
		self._cr.execute("""SELECT account_move_line.id, act.type, SUM(account_move_line.amount_residual)
						FROM """ + tables + """
						LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
						LEFT JOIN account_account_type act ON (a.user_type_id=act.id)
						WHERE act.type IN ('receivable','payable')
						AND account_move_line.partner_id IN %s
						AND account_move_line.reconciled IS NOT TRUE
						""" + where_clause + """
						GROUP BY account_move_line.id, act.type
						""", where_params)
		credit, debit = [], []
		for pid, type, val in self._cr.fetchall():
			move = self.env['account.move.line'].browse(pid)
			if type == 'receivable':
				credit.append(_('Number %s - %s'%(move.move_id.name, move.date_maturity)))
			elif type == 'payable':
				debit.append(_('Number %s - %s'%(move.move_id.name, move.date_maturity)))

		return credit, debit
