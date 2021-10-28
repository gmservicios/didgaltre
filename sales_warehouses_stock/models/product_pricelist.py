# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class Pricelist(models.Model):
    _inherit = "product.pricelist"

    view_all = fields.Boolean(string="View All", default=False)
