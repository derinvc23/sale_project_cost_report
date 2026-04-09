# -*- coding: utf-8 -*-
{
    'name': u'Reporte de Costos y Márgenes por Proyecto',
    'version': '10.0.1.0.0',
    'category': 'Sales',
    'summary': u'Reporte de costos, ingresos y márgenes por Orden de Venta / Proyecto',
    'author': 'Aluminios de Bolivia',
    'depends': [
        'sale',
        'sale_stock',
        'account',
        'sale_material_no_facturable',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_cost_wizard_view.xml',
        'views/sale_cost_report_view.xml',
        'views/sale_material_nf_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
