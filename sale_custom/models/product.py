from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    standard_price = fields.Float(groups="sale_custom.group_view_cost_price")

class ProductProduct(models.Model):
    _inherit = "product.product"

    standard_price = fields.Float(groups="sale_custom.group_view_cost_price")