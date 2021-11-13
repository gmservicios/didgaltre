# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    amount_due = fields.Monetary(string="Amount due", currency_field='currency_id', store=True, readonly=True,
        compute='_compute_amount')
    amount_payment = fields.Monetary(string="Amount payment", currency_field="currency_id")
    amount_refund = fields.Monetary(compute="_compute_amount_return", string="Amount refund", currency_field="currency_id", readonly=True, store=True)

    @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id', 'payment_date')
    def _compute_amount(self):
        super(AccountPaymentRegister, self)._compute_amount()
        if not self._context.get("amount_payment",False):
            for wizard in self:
                if wizard.source_currency_id == wizard.currency_id:
                    # Same currency.
                    wizard.amount_due = wizard.source_amount_currency
                elif wizard.currency_id == wizard.company_id.currency_id:
                    # Payment expressed on the company's currency.
                    wizard.amount_due = wizard.source_amount
                else:
                    # Foreign currency on payment different than the one set on the journal entries.
                    amount_payment_currency = wizard.company_id.currency_id._convert(wizard.source_amount, wizard.currency_id, wizard.company_id, wizard.payment_date)
                    wizard.amount_due = amount_payment_currency

    @api.depends("amount_payment", "amount")
    def _compute_amount_return(self):
        for wiz in self:
            wiz.amount_refund = wiz.amount_payment - wiz.amount

    @api.onchange('amount_payment')
    def _onchange_amount_payment(self):
        if self.amount_payment >= self.amount:
            self.with_context(amount_payment=True)._compute_amount()
        else:
            self.amount = self.amount_payment
    

    # @api.model
    # def default_get(self, fields_list):
    #     res = super().default_get(fields_list)
    #     if 'line_ids' in fields_list and line_ids not in res:
    #         raise UserError(_("You can't not register"))
    #     return res