from datetime import timedelta

from odoo import api, exceptions, fields, models


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate property offer model"

    price = fields.Float("Price")
    status = fields.Selection(
        [("accepted", "Accepted"), ("refused", "Refused")], "Status", copy=False
    )
    partner_id = fields.Many2one("res.partner", "Buyer", required=True)
    property_id = fields.Many2one("estate.property", required=True)

    validity = fields.Integer("Validity (days)", default=7)
    date_deadline = fields.Date(
        "Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline"
    )

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = (
                record.create_date.date() if record.create_date else fields.Date.today()
            ) + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (
                record.date_deadline - record.create_date.date()
                if record.create_date
                else fields.Date.today()
            ).days

    def action_accept(self):
        if len(self) > 1:
            raise exceptions.UserError("Only one offer can be accepted.")
        for record in self:
            record.status = "accepted"
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
        return True

    def action_refuse(self):
        for record in self:
            record.status = "refused"

        return True
