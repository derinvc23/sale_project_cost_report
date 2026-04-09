# -*- coding: utf-8 -*-
import time
from odoo import api, fields, models


class SaleCostWizard(models.TransientModel):
    _name = 'sale.cost.wizard'
    _description = u'Filtros Reporte Costos y Márgenes'

    date_from = fields.Date(
        string='Desde',
        required=True,
        default=lambda *a: time.strftime('%Y-%m-01'),  # primer día del mes actual
    )
    date_to = fields.Date(
        string='Hasta',
        required=True,
        default=lambda *a: time.strftime('%Y-%m-%d'),
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        domain=[('customer', '=', True)],
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Sucursal',
    )

    @api.multi
    def action_view_report(self):
        self.ensure_one()
        domain = [
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
        ]
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        if self.warehouse_id:
            domain.append(('warehouse_id', '=', self.warehouse_id.id))

        search_view = self.env.ref(
            'sale_project_cost_report.view_sale_project_cost_report_search'
        )
        return {
            'type': 'ir.actions.act_window',
            'name': u'Costos y Márgenes por Proyecto',
            'res_model': 'sale.project.cost.report',
            'view_type': 'tree',
            'view_mode': 'tree',
            'domain': domain,
            'context': {},
            'search_view_id': [search_view.id, search_view.name],
            'target': 'current',
        }
