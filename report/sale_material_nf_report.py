# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class SaleMaterialNfReport(models.Model):
    _name = 'sale.material.nf.report'
    _description = u'Detalle de Materiales No Facturables por Proyecto'
    _auto = False
    _order = 'date_order desc, order_name'

    order_id = fields.Many2one('sale.order', string=u'Orden de Venta', readonly=True)
    order_name = fields.Char(string=u'N° OV', readonly=True)
    invoice_name = fields.Char(string=u'N° Factura', readonly=True)
    invoice_date = fields.Date(string='Fecha Factura', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', readonly=True)
    date_order = fields.Date(string='Fecha OV', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Sucursal', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', readonly=True)
    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    product_categ_id = fields.Many2one('product.category', string=u'Categoría', readonly=True)
    uom_id = fields.Many2one('product.uom', string='Unidad', readonly=True)
    kg_weight = fields.Float(string='Peso Total (Kg)', readonly=True, group_operator='sum')
    qty = fields.Float(string='Cantidad', readonly=True, group_operator='sum')
    costo_material = fields.Float(string='Costo Unit.', readonly=True, group_operator='avg')
    costo_total = fields.Float(string='Costo Total', readonly=True, group_operator='sum')
    precio_venta = fields.Float(string='Precio Venta', readonly=True, group_operator='avg')
    descuento = fields.Float(string='Descuento %', readonly=True, group_operator='avg')
    precio_con_descuento = fields.Float(string='Precio con Des.', readonly=True, group_operator='avg')
    importe_facturado = fields.Float(string='Total Facturado', readonly=True, group_operator='avg')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'sale_material_nf_report')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW sale_material_nf_report AS (
                SELECT
                    sol.id                          AS id,
                    so.id                           AS order_id,
                    so.name                         AS order_name,
                    inv.invoice_number              AS invoice_name,
                    inv.invoice_date                AS invoice_date,
                    so.partner_id                   AS partner_id,
                    so.date_order::date             AS date_order,
                    so.warehouse_id                 AS warehouse_id,
                    ppl.currency_id                 AS currency_id,
                    sol.product_id                  AS product_id,
                    pt.categ_id                     AS product_categ_id,
                    sol.product_uom                 AS uom_id,
                    pt.kg_weight * sol.product_uom_qty AS kg_weight,
                    sol.product_uom_qty             AS qty,
                    sol.costo_material              AS costo_material,
                    sol.product_uom_qty * sol.costo_material AS costo_total,
                    pt.list_price                    AS precio_venta,
                    sol.discount                    AS descuento,
                    pt.list_price * (1 - COALESCE(sol.discount, 0) / 100) AS precio_con_descuento,
                    COALESCE(inv.importe_facturado, 0) AS importe_facturado
                FROM sale_order so
                JOIN sale_order_line sol ON sol.order_id = so.id
                JOIN product_product pp  ON pp.id = sol.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN product_pricelist ppl ON ppl.id = so.pricelist_id
                LEFT JOIN (
                    SELECT DISTINCT ON (ai.origin)
                           ai.origin         AS sale_name,
                           ai.number         AS invoice_number,
                           ai.date_invoice   AS invoice_date,
                           ai.amount_total   AS importe_facturado
                    FROM account_invoice ai
                    WHERE ai.type = 'out_invoice'
                      AND ai.state NOT IN ('cancel', 'draft')
                    ORDER BY ai.origin, ai.date_invoice DESC
                ) inv ON inv.sale_name = so.name
                WHERE so.state IN ('sale', 'done')
                  AND sol.no_facturable = true
            )
        """)
