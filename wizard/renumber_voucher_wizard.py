from odoo import api, exceptions, fields, models, _


class RenumberVoucherWizard(models.TransientModel):
    _name = "renumber.voucher.wizard"
    _description = "Renumber Voucher"

    posted_only = fields.Boolean(
        default=False,
    )
    continuation = fields.Boolean(
        default=False,
    )
    starting_number = fields.Integer(
        default=1, help="Reset sequence to this number before starting."
    )
    word_id = fields.Many2one(
        "account.cn.voucher.word",
        required=True,
    )
    sequence_id = fields.Many2one(related="word_id.voucher_number_sequence_id")
    date_range_ids = fields.Many2many(
        "ir.sequence.date_range",
        required=True,
        domain="[('sequence_id', '=', sequence_id)]",
    )
    accounting_book_id = fields.Many2one(
        "account.cn.accounting.book",
    )
    voucher_type_id = fields.Many2one(
        "account.cn.voucher.type",
    )
    # numbering = fields.Selection(
    #     selection=[
    #         ("book_first", "Accounting Book First"),
    #         ("type_first", "Voucher Type First"),
    #     ],
    # )

    def renumber_voucher(self):
        if self.date_range_ids:
            base_domain = []
            base_domain += [("word_id", "=", self.word_id.id)]
            if self.posted_only:
                base_domain += [("state", "=", "posted")]
            if self.accounting_book_id:
                base_domain += [("accounting_book_id", "=", self.accounting_book_id.id)]
            if self.voucher_type_id:
                base_domain += [("voucher_type_id", "=", self.voucher_type_id.id)]
            for dr in self.date_range_ids:
                domain = []
                domain += base_domain
                domain += [("date", ">=", dr.date_from), ("date", "<=", dr.date_to)]
                vouchers = self.env["account.cn.voucher"].search(
                    domain,
                    order="date, id",
                )
                if not vouchers:
                    raise exceptions.UserError(_("No vouchers found."))
                if not self.continuation:
                    dr.number_next = self.starting_number
                for voucher in vouchers:
                    voucher.number = dr.sequence_id.next_by_id(voucher.date)
        else:
            raise exceptions.UserError(_("Date range is empty."))
