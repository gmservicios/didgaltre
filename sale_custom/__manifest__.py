# -*- coding: utf-8 -*-
{
    'name': "Module Sale Custom",
    'summary': "Adecuaciones a ventas e inventarios",
    'description': """
        > Desarrollo en Ventas-Inventario, al crear el picking desde ventas, este tiene que estar reservada la totalidad de cantidad de venta solicitada
        """,
    'author': "Gustavo H.",
    'category': 'Sales/Sales',
    'version': '1.0.1',
    'depends': ['sale_stock','stock'],
    'qweb': [
    ],
    'data': [
        "security/user_groups.xml",
        "security/ir.model.access.csv",
        "views/res_users_view.xml",
        "views/product_view.xml",
        "views/res_partner_view.xml",
        "views/payment_term_view.xml",
        "views/sale_order_view.xml",
        "views/account_move_view.xml",
        "wizard/account_payment_register_wiz.xml",
        "wizard/account_payment_make_before_billing_wiz.xml",
    ],
    'installable': True,
    'auto_install': True,
}