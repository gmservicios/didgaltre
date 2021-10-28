from odoo import models, fields, api, _
from odoo.tools import float_repr
import logging
_logger = logging.getLogger(__name__)

class Pricelist(models.Model):
    _inherit = "product.pricelist"
    _order = "name asc, sequence asc, id desc"

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_information_from_js(self, product_id, company_id, partner):
        _logger.info('\nget_information_from_js\n %r \n\n', partner)
        if not product_id:
            return {}
        decimal_places = self.env['decimal.precision'].precision_get('Product Price')
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        product = self.env['product.product'].browse(product_id)
        groupe_per_location = {}
        groupe_per_pricelist = {}

        for stock_quant_id in product.stock_quant_ids.filtered(lambda sq: sq.location_id.usage == 'internal'):
            groupe_per_location.setdefault(stock_quant_id.location_id, {'name': stock_quant_id.location_id.display_name,'qty':0.0,'visible':True})
            warehouse = stock_quant_id.location_id.get_warehouse()
            if not warehouse.visible_on_sol:
                groupe_per_location[stock_quant_id.location_id]['visible'] = False
            groupe_per_location[stock_quant_id.location_id]['qty'] += float(float_repr(stock_quant_id.quantity, precision))

        domain = [
            '&',('pricelist_id.view_all', '=', True) ,
            '&',('company_id', 'in', [company_id, False]) ,
            '|',
            '&', ('product_tmpl_id', '=', product.product_tmpl_id.id), ('applied_on', '=', '1_product'),
            '&', ('product_id', '=', product.id), ('applied_on', '=', '0_product_variant')]
        pricelists = self.env['product.pricelist.item'].search(domain)
        if pricelists:
            pricelists = pricelists.sorted(lambda pl: pl.pricelist_id.name)
        pricelist = False
        if partner:
            partner_obj = self.env['res.partner'].browse(partner.get('id'))
            pricelist = partner_obj.property_product_pricelist.mapped('item_ids').filtered(lambda pp: 
                (pp.product_tmpl_id.id == product.product_tmpl_id.id and pp.applied_on == '1_product')
                 or 
                (pp.product_id.id == product.id and pp.applied_on == '0_product_variant'))
            _logger.info('\n\n %r \n\n', [partner_obj,partner_obj.property_product_pricelist, pricelist])
            for pl in pricelist:
                price = "%s %s" % (
                            pl.currency_id.symbol,
                            float_repr(
                                pl.fixed_price,
                                decimal_places,
                            ),
                        )
                qty = "%s" % (
                            float_repr(
                                pl.min_quantity,
                                precision,
                            ),
                        )
                groupe_per_pricelist.setdefault(pl.id,{'name':pl.pricelist_id.name, 'min_quantity': qty, 'fixed_price': price})

        for pl in pricelists:
            if pl in pricelist:
                continue
            price = "%s %s" % (
                        pl.currency_id.symbol,
                        float_repr(
                            pl.fixed_price,
                            decimal_places,
                        ),
                    )
            qty = "%s" % (
                        float_repr(
                            pl.min_quantity,
                            precision,
                        ),
                    )
            groupe_per_pricelist.setdefault(pl.id,{'name':pl.pricelist_id.name, 'min_quantity': qty, 'fixed_price': price})
        return {
            'name': product.display_name,
            'qty_available': product.qty_available,
            'virtual_available': product.virtual_available,
            'uom': product.uom_id.name,
            'qty_per_location': list(groupe_per_location.values()) or False,
            'pricelist_items': list(groupe_per_pricelist.values()) or False,
        }
