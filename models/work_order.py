from odoo import models, fields, api, _

class WorkOrder(models.Model):
    _name = 'work.order'
    _description = 'Orden de Trabajo'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Habilita el chatter


    title = fields.Char(string="Título", required=True)
    order_number = fields.Char(string="Número de Orden", readonly=True, copy=False, default='New')
    value = fields.Monetary(string="Valor de la Orden", compute="_compute_value", store=True, currency_field='currency_id')
    client_id = fields.Many2one('res.partner', string="Cliente", required=True)
    worker_id = fields.Many2one('hr.employee', string="Trabajador")
    product_ids = fields.One2many('work.order.product', 'work_order_id', string="Productos")
    currency_id = fields.Many2one('res.currency', string='Moneda')
    date = fields.Date(string="Fecha")
    address = fields.Char(string="Dirección", related='client_id.street', readonly=False)
    city = fields.Char(string="Ciudad", related='client_id.city', readonly=False)
    time_block = fields.Char(string="Bloque Horario")

    image_ids = fields.One2many('work.order.image', 'work_order_id', string="Imágenes")
    sale_order_id = fields.Many2one('sale.order', string="Pedido de Ventas", tracking=True)

    state = fields.Selection([
            ('draft', 'Borrador'),
            ('in_progress', 'En Progreso'),
            ('done', 'Terminado'),
            ('cancel', 'Cancelado'),
        ], string="Estado", default='draft', tracking=True)



    @api.depends('product_ids')
    def _compute_value(self):
        for order in self:
            order.value = sum(product.subtotal for product in order.product_ids)

    # Método para enviar la orden por correo
    def action_send_order_by_email(self):
        template_id = self.env.ref('my_order_module.email_template_work_order').id
        self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    # Método para generar el número de orden automáticamente
    @api.model
    def create(self, vals):
        if vals.get('order_number', 'New') == 'New':
            vals['order_number'] = self.env['ir.sequence'].next_by_code('work.order.sequence') or 'New'
        return super(WorkOrder, self).create(vals)
    
    # Método para cambiar el estado
    def action_set_in_progress(self):
        self.state = 'in_progress'

    def action_set_done(self):
        self.state = 'done'

    def action_set_cancel(self):
        self.state = 'cancel'






class WorkOrderProduct(models.Model):
    _name = 'work.order.product'
    _description = 'Producto de Orden de Trabajo'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Habilita el chatter


    work_order_id = fields.Many2one('work.order', string="Orden de Trabajo", required=True)
    product_id = fields.Many2one('product.product', string="Producto", required=True)
    quantity = fields.Float(string="Cantidad", required=True)
    price_unit = fields.Float(string="Precio Unitario", related='product_id.list_price', readonly=True)
    subtotal = fields.Monetary(string="Subtotal", compute="_compute_subtotal", store=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Moneda')

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit


class WorkOrderPayment(models.Model):
    _name = 'work.order.payment'
    _description = 'Pago de Orden de Trabajo'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Habilita el chatter


    name = fields.Char(string="Referencia", required=True, copy=False, readonly=True, default=lambda self: _('New'))
    worker_id = fields.Many2one('hr.employee', string="Trabajador", required=True)
    start_date = fields.Date(string="Fecha de Inicio", required=True)
    end_date = fields.Date(string="Fecha de Fin", required=True)
    order_ids = fields.Many2many('work.order', string="Órdenes de Trabajo")
    total_amount = fields.Monetary(string="Monto Total", compute="_compute_total_amount", store=True, currency_field='currency_id')
    is_paid = fields.Boolean(string="Pagado", default=False)
    currency_id = fields.Many2one('res.currency', string='Moneda', required=True, default=lambda self: self.env.company.currency_id)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('work.order.payment') or _('New')
        return super(WorkOrderPayment, self).create(vals)

    @api.depends('order_ids')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(order.value for order in record.order_ids)

    @api.onchange('worker_id', 'start_date', 'end_date')
    def _onchange_worker_and_dates(self):
        if self.worker_id and self.start_date and self.end_date:
            self.order_ids = self.env['work.order'].search([
                ('worker_id', '=', self.worker_id.id),
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
            ])
