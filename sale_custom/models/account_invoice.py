from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
	_inherit = "account.move"

	to_approve = fields.Boolean(string="To Approve", default=False)

	def action_post(self):
		res = self._action_register_payment_validate()
		if res and not self._context.get('payment', False):
			return res
		return super(AccountMove, self).action_post()

	def _action_register_payment_validate(self):
		ctx = self._context or {}
		for inv in self.filtered(lambda i: i.state == 'draft' and i.move_type in ('out_invoice')):
			# if inv.to_approve and self.env.user.has_group('sale_custom.group_approve_credit_exception'):
			if inv.to_approve and (self.env.user.has_group('sale_custom.group_approve_credit_exception') or self.env.user.id == self.invoice_user_id.approval_manager_id.id):
				inv.write({'to_approve':False})
				continue
			if inv.invoice_payment_term_id.payment_method == 'credit' and inv.partner_id.check_credit:
				inv.partner_id._check_credit_debit_limit(inv.amount_total, inv.invoice_date, 'receivable')
			elif inv.invoice_payment_term_id.payment_method == 'counted':
				return self.action_register_payment_make_before_billing()
		return False

	def action_send_to_approve(self):
		msg = _("""
				Hello<br/>
				Validate aproval of <a href='#' data-oe-model='%s' data-oe-id='%d'>invoice Draft</a> of order %s for customer <strong>%s</strong>""" % (
				self._name, self.id, self.invoice_origin or 'S/N', self.partner_id.display_name))
		self._create_mail_channel_private_approve(msg)
		self.write({'to_approve':True})

	def action_credit_debit_approve(self):
		res = self.action_post()
		msg = _("""
				Hello<br/>
				<strong>[APPROVED] Invoice <a href='#' data-oe-model='%s' data-oe-id='%d'>%s</a></strong> for order %s, for customer <strong>%s</strong>""" % (
				self._name, self.id, self.name, self.invoice_origin or 'S/N', self.partner_id.display_name))
		self._create_mail_channel_private_approve(msg, to_approved=False)
		return res

	def _create_mail_channel_private_approve(self, message, to_approved=True):
		users = self.env['res.users'].search([]).filtered(lambda ru: ru.has_group('sale_custom.group_approve_credit_exception'))
		partners = users.mapped('partner_id')
		if to_approved and self.invoice_user_id.approval_manager_id:
			partners |= self.invoice_user_id.approval_manager_id.partner_id
		partner_from = to_approved and self.invoice_user_id.partner_id or self.env.user.partner_id
		if not partners:
			raise UserError(_("There is no designated users for this operation"))
		if not to_approved:
			partners |= self.invoice_user_id.partner_id
		channel_approve = self.env['mail.channel'].channel_get(partners_to=partners.ids)
		channel = self.env['mail.channel'].browse(channel_approve['id'])
		channel.message_post(body=message, author_id=partner_from.id, message_type="comment", subtype_xmlid="mail.mt_comment")

	def action_register_payment_make_before_billing(self):
		''' Open the account.payment.register wizard to pay the selected journal entries.
		:return: An action opening the account.payment.register wizard.
		'''
		return {
			'name': _('Register Payment Make Before Billing'),
			'res_model': 'account.payment.make.before.billing',
			'view_mode': 'form',
			'context': {
				'active_model': 'account.move',
				'active_ids': self.ids,
				'draft_move': True
			},
			'target': 'new',
			'type': 'ir.actions.act_window',
		}