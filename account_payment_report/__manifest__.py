# -*- coding: utf-8 -*-
{
    'name': "Report Cash End Payment",
    'summary': "Reporte de cierre de caja",
    'author': "Gustavo H.",
    'version': '1.0.0',
    'depends': ['account', 'sale_custom'],
    'qweb': [
    ],
    'data': [
        "security/ir.model.access.csv",
        "wizard/account_payment_report_wiz.xml",
        "views/report_payment_cash.xml",
        "views/account_reports.xml",
    ],
}