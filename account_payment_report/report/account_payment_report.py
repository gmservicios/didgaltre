# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ReportJournal(models.AbstractModel):
    _name = 'report.account_payment_report.report_payment_cash_end'
    _description = 'Account Payment report'

    def get_journals(self, payments):
        journal = payments.mapped('journal_id')
        return journal

    def get_values(self, data):
        dic = {}
        invoices = self._get_query_invoice(data)
        payments = self._get_query_payment(data)
        # counted = []
        # nc = []
        # credit = []
        # receipt = []
        invoice_obj = self.env['account.move']
        jnal = self.env['account.journal']
        # journals = {'counted':[jnal,[],[]],'nc':[jnal,[],[]],'credit':[jnal,[],[]],'receipt':[jnal,[],[]]}
        journals = {}

        for ap in payments:
            for inv in ap.reconciled_invoice_ids.filtered(lambda i: i.move_type in ['out_invoice','out_refund']):
                code = inv.move_type + inv.invoice_payment_term_id.payment_method
                vals = {
                    'name': inv.invoice_payment_term_id.payment_method,
                    ap.journal_id.id: ap.amount,
                    'date': ap.date,
                    'partner': inv.partner_id.name,
                    'pay_number': ap.name,
                    'doc_number': inv.name,
                    'total': ap.amount
                    }
                if inv.move_type == 'out_invoice' and inv.invoice_payment_term_id.payment_method == 'counted':
                    type = 'counted';
                    journals.setdefault(type,[jnal,[],{},_("CONTADO"),0.0])
                elif inv.move_type == 'out_invoice' and inv.invoice_payment_term_id.payment_method == 'credit':
                    type = 'receipt';
                    journals.setdefault(type,[jnal,[],{},_("RECIBO"),0.0])
                else:
                    type = 'nc'
                    journals.setdefault(type,[jnal,[],{},_("NC DEVOLUCION"),0.0])

                journals[type][0] |= ap.journal_id
                journals[type][1].append(vals)
                journals[type][2].setdefault(ap.journal_id.id, 0.0)
                journals[type][2][ap.journal_id.id] += ap.amount
                journals[type][4] += ap.amount

                invoice_obj |= inv

        if invoices and invoice_obj:
            invoices -= invoice_obj
        for inv in invoices:
            vals = {
                'name': inv.invoice_payment_term_id.payment_method,
                inv.journal_id.id: inv.amount_total,
                'date': inv.invoice_date,
                'partner': inv.partner_id.name,
                'pay_number': False,
                'doc_number': inv.name,
                'total': inv.amount_total
                }
            if inv.move_type == 'out_invoice':
                type = 'credit'
                journals.setdefault(type,[jnal,[],{},_("CREDITOS"),0.0])
            else:
                type = 'nc_f'
                vals.update({'pay_number': inv.reversed_entry_id and inv.reversed_entry_id.name or False})
                journals.setdefault(type,[jnal,[],{},_("NC-FAC"),0.0])

            journals[type][0] |= inv.journal_id
            journals[type][1].append(vals)
            journals[type][2].setdefault(inv.journal_id.id, 0.0)
            journals[type][2][inv.journal_id.id] += inv.amount_total
            journals[type][4] += ap.amount
        # return  counted, credit, receipt, nc, journals
        return  journals

    def _get_query_payment(self, data):
        res_ap = self.env['account.payment'].search([
            ('state','=','posted'),
            ('date','>=',data['form'].get('date_from')),
            ('date','<=',data['form'].get('date_to')),
            ('create_uid','=',data['form'].get('user_id')[0]),
            ('company_id','=',data['form'].get('company_id')[0])
            ])
        return res_ap

    def _get_query_invoice(self, data):
        res_ap = self.env['account.move'].search([
            ('invoice_date','>=',data['form'].get('date_from')),
            ('invoice_date','<=',data['form'].get('date_to')),
            ('state','=','posted'),
            ('invoice_payment_term_id.payment_method','=','credit'),
            ('invoice_user_id','=',data['form'].get('user_id')[0]),
            ('move_type','in',('out_invoice','out_refund')),
            ('company_id','=',data['form'].get('company_id')[0])
            ])
        return res_ap

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        journals = self.get_values(data)
        _logger.info('\ndata\n %r \n\n', journals)
        return {
            'user': self.env['res.users'].browse(data['form']['user_id'][0]),
            'doc_model': 'account.payment.report',
            'data': data,
            'docs': self.env['account.payment.report'].browse(data['form']['id']),
            # 'counted' : counted,
            # 'credit' : credit,
            # 'receipt' : receipt,
            # 'nc' : nc,
            'journals' : journals,
            'company_id': self.env['res.company'].browse(
                data['form']['company_id'][0]),
        }
