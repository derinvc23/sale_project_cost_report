# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class SaleMaterialNfReport(models.Model):
    _name = 'sale.material.nf.report'
    _description = u'Detalle de Materiales No Facturables por Proyecto'
    _auto = False
    _order = 'date_order desc, order_name'

    order_id = fields.Many2one('sale.order', string=u'Orden de Venta', readonly=True)
    order_name = fields.Char(string=u'N° OV', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', readonly=True)
    date_order = fields.Date(string='Fecha OV', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Sucursal', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', readonly=True)
    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    product_categ_id = fields.Many2one('product.category', string=u'Categoría', readonly=True)
    uom_id = fields.Many2one('product.uom', string='Unidad', readonly=True)
    qty = fields.Float(string='Cantidad', readonly=True)
    costo_material = fields.Float(string='Costo Unit.', readonly=True)
    costo_total = fields.Float(string='Costo Total', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'sale_material_nf_report')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW sale_material_nf_report AS (
                SELECT
                    sol.id                          AS id,
                    so.id                           AS order_id,
                    so.name                         AS order_name,
                    so.partner_id                   AS partner_id,
                    so.date_order::date             AS date_order,
                    so.warehouse_id                 AS warehouse_id,
                    so.currency_id                  AS currency_id,
                    sol.product_id                  AS product_id,
                    pt.categ_id                     AS product_categ_id,
                    sol.product_uom                 AS uom_id,
                    sol.product_uom_qty             AS qty,
                    sol.costo_material              AS costo_material,
                    sol.product_uom_qty * sol.costo_material AS costo_total
                FROM sale_order so
                JOIN sale_order_line sol ON sol.order_id = so.id
                JOIN product_product pp  ON pp.id = sol.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                WHERE so.state IN ('sale', 'done')
                  AND sol.no_facturable = true
            )
        """)
