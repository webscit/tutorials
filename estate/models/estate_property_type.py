from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate property type model"

    name = fields.Char("Title", required=True)

    _unique_name = models.Constraint(
        "UNIQUE(name)",
        "A property type name must be unique"
    )
