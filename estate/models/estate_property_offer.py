from odoo import fields, models


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate property offer model"

    price = fields.Float("Price")
    status = fields.Selection(
        [("accepted", "Accepted"), ("refused", "Refused")], "Status", copy=False
    )
    partner_id = fields.Many2one("res.partner", "Buyer", required=True)
    property_id = fields.Many2one("estate.property", required=True)
