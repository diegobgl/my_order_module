{
    'name': 'Ordenes de Trabajo Mejoradas',
    'version': '1.0',
    'category': 'Operations/Project',
    'author': 'Diego Gajardo',
    'website': 'www.dgdev.cl',

    'summary': 'Gestión de órdenes de trabajo con liquidación de pagos',
    'description': """
        Este módulo extiende la funcionalidad de gestión de órdenes de trabajo, 
        permitiendo la asignación de productos, trabajadores y la generación de reportes de liquidación de pagos.
    """,
    'depends': ['base', 'hr', 'product'],
    'data': [
        'data/ir_sequence_data.xml',  
        'report/order_report.xml',
        'report/work_order_payment_report_template.xml',
        'report/work_order_payment_report.xml',
        'report/order_report_template.xml',
        'security/ir.model.access.csv',
        'views/order_views.xml',
        'views/email_template.xml'
    ],
    'installable': True,
    'application': True,
}

