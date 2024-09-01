from odoo import models, fields

class WorkOrderImage(models.Model):
    _name = 'work.order.image'
    _description = 'Work Order Image'

    # Relación con la orden de trabajo
    work_order_id = fields.Many2one('work.order', string="Orden de Trabajo", required=True, ondelete='cascade')
    
    # Campo de imagen
    image = fields.Image(string="Imagen")
    description = fields.Char(string="Descripción")
