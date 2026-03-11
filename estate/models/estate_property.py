from datetime import timedelta

from odoo import fields, models


def _default_date_availability(*args):
    return fields.Date.today() + timedelta(days=365.25 / 4)


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate property model"

    name = fields.Char("Title", required=True)
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        copy=False,
        default="new",
    )

    description = fields.Text("Description")
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    property_tag_ids = fields.Many2many("estate.property.tag", string="Property Tags")

    postcode = fields.Char("Post Code")
    date_availability = fields.Date(
        "Available From", copy=False, default=_default_date_availability
    )
    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float("Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer("Bedrooms", default=2)
    living_area = fields.Integer("Living area (sqm)")
    facades = fields.Integer("# Facades")
    garage = fields.Boolean("Has a garage")
    garden = fields.Boolean("Has a graden")
    garden_area = fields.Integer("Garden area")
    garden_orientation = fields.Selection(
        string="Garden orientation",
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
    )

    salesperson_id = fields.Many2one(
        "res.users", string="Salesperson", default=lambda self: self.env.user
    )
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)

    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
