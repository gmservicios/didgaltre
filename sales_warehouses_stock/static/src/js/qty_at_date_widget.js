odoo.define('sales_warehouses_stock.QtyAtDateWidget', function (require) {
"use strict";

var sale_stock = require('sale_stock.QtyAtDateWidget');

var core = require('web.core');
var QWeb = core.qweb;

var Widget = require('web.Widget');
var widget_registry = require('web.widget_registry');
var utils = require('web.utils');

var _t = core._t;
var time = require('web.time');


sale_stock.include({
    events: _.extend({}, Widget.prototype.events, {
        'click .fa-area-chart': '_onClickButton',
    }),

    _getContentRes(result) {
        if (!this.data.scheduled_date) {
            return;
        }
        this.data.delivery_date = this.data.scheduled_date.clone().add(this.getSession().getTZOffset(this.data.scheduled_date), 'minutes').format(time.getLangDateFormat());
        if (this.data.forecast_expected_date) {
            this.data.forecast_expected_date_str = this.data.forecast_expected_date.clone().add(this.getSession().getTZOffset(this.data.forecast_expected_date), 'minutes').format(time.getLangDateFormat());
        }   
        result['data'] = this.data
        const $content = $(QWeb.render('sale_stock.QtyDetailPopOver', result));
        $content.on('click', '.action_open_forecast', this._openForecast.bind(this));
        return $content;
    },

    _setPopOver() {
        var self = this;
        if (!this.data.scheduled_date) {
            return;
        }
        if (this.data.product_id) {
            this._rpc({
                model: 'product.product',
                method: 'get_information_from_js',
                args: [this.data.product_id.data.id, this.data.company_id.data.id, this.data.partner_id.data],
            }, { asyc: false }).then(function(result) {
                result['data'] = self.data;
                const $content = self._getContentRes(result); //$(QWeb.render('sale_stock.QtyDetailPopOver', result));
                const options = {
                    content: $content,
                    html: true,
                    placement: 'left',
                    title: _t('Information'),
                    trigger: 'focus',
                    delay: { 'show': 0, 'hide': 100 },
                };
                self.$el.popover(options);
            });
        } else{
            this._super();
        }
    },

});

});
