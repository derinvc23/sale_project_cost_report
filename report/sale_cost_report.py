# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class SaleProjectCostReport(models.Model):
    _name = 'sale.project.cost.report'
    _description = u'Reporte Costos y Márgenes por Proyecto'
    _auto = False
    _order = 'date_order desc'

    order_id = fields.Many2one('sale.order', string=u'Orden de Venta', readonly=True)
    order_name = fields.Char(string=u'N° OV', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', readonly=True)
    date_order = fields.Date(string='Fecha', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Sucursal', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', readonly=True)
    ingreso = fields.Float(string='Ingreso', readonly=True,
                           help=u'Suma de las líneas facturables (precio subtotal)')
    costo = fields.Float(string='Costo Materiales', readonly=True,
                         help=u'Suma de materiales no facturables (cantidad × costo unitario)')
    margen = fields.Float(string='Margen', readonly=True,
                          help='Ingreso - Costo Materiales')
    margen_pct = fields.Float(string='Margen %', readonly=True,
                               help=u'Margen / Ingreso × 100')
    cant_materiales = fields.Integer(string=u'# Mat. NF', readonly=True,
                                     help=u'Cantidad de líneas de material no facturable')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'sale_project_cost_report')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW sale_project_cost_report AS (
                SELECT
                    so.id                                               AS id,
                    so.id                                               AS order_id,
                    so.name                                             AS order_name,
                    so.partner_id                                       AS partner_id,
                    so.date_order::date                                 AS date_order,
                    so.warehouse_id                                     AS warehouse_id,
                    ppl.currency_id                                     AS currency_id,

                    /* Ingresos: suma de líneas facturables */
                    COALESCE(
                        SUM(CASE WHEN sol.no_facturable = false
                                 THEN sol.price_subtotal ELSE 0 END),
                        0
                    )                                                   AS ingreso,

                    /* Costo: suma de materiales no facturables */
                    COALESCE(
                        SUM(CASE WHEN sol.no_facturable = true
                                 THEN sol.product_uom_qty * sol.costo_material
                                 ELSE 0 END),
                        0
                    )                                                   AS costo,

                    /* Margen = Ingreso - Costo */
                    COALESCE(
                        SUM(CASE WHEN sol.no_facturable = false
                                 THEN sol.price_subtotal ELSE 0 END),
                        0
                    ) -
                    COALESCE(
                        SUM(CASE WHEN sol.no_facturable = true
                                 THEN sol.product_uom_qty * sol.costo_material
                                 ELSE 0 END),
                        0
                    )                                                   AS margen,

                    /* Margen % */
                    CASE
                        WHEN COALESCE(
                            SUM(CASE WHEN sol.no_facturable = false
                                     THEN sol.price_subtotal ELSE 0 END), 0
                        ) = 0 THEN 0
                        ELSE ROUND(
                            (
                                COALESCE(
                                    SUM(CASE WHEN sol.no_facturable = false
                                             THEN sol.price_subtotal ELSE 0 END),
                                    0
                                ) -
                                COALESCE(
                                    SUM(CASE WHEN sol.no_facturable = true
                                             THEN sol.product_uom_qty * sol.costo_material
                                             ELSE 0 END),
                                    0
                                )
                            )::numeric
                            /
                            NULLIF(
                                COALESCE(
                                    SUM(CASE WHEN sol.no_facturable = false
                                             THEN sol.price_subtotal ELSE 0 END),
                                    0
                                ), 0
                            )::numeric * 100,
                            2
                        )
                    END                                                 AS margen_pct,

                    /* Cantidad de líneas no facturables */
                    COUNT(CASE WHEN sol.no_facturable = true THEN 1 END)::integer
                                                                        AS cant_materiales

                FROM sale_order so
                LEFT JOIN sale_order_line sol ON sol.order_id = so.id
                LEFT JOIN product_pricelist ppl ON ppl.id = so.pricelist_id
                WHERE so.state IN ('sale', 'done')
                GROUP BY
                    so.id, so.name, so.partner_id, so.date_order,
                    so.warehouse_id, ppl.currency_id
            )
        """)
