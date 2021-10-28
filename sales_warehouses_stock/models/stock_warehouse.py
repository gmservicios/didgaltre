from odoo import _, api, fields, models

class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    visible_on_sol = fields.Boolean(string="Visible on Sale order line", default=True)