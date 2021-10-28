# -*- coding: utf-8 -*-
from odoo import models, fields

class Users(models.Model):
    _inherit = ['res.users']

    approval_manager_id = fields.Many2one('res.users', string='Approval Manager')
    user_aprobals = fields.One2many('res.users', 'approval_manager_id', string='Users Childs')
    # approval_manager = fields.Boolean(string="Approval Admin", default=False)

    restrict_locations = fields.Boolean('Restrict Location')
    stock_location_ids = fields.Many2many(
        'stock.location',
        'location_security_stock_location_users',
        'user_id',
        'location_id',
        'Stock Locations')
    default_picking_type_ids = fields.Many2many(
        'stock.picking.type', 'stock_picking_type_users_rel',
        'user_id', 'picking_type_id', string='Default Warehouse Operations')

    def write(self, values):
        res = super(Users, self).write(values)
        if 'default_picking_type_ids' in values or 'stock_location_ids' in values:
            self.env['ir.model.access'].call_cache_clearing_methods()
            self.env['ir.rule'].clear_caches()
            self.has_group.clear_cache(self)
        return res