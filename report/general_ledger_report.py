import calendar
import datetime

from odoo import api, fields, models, _
from odoo.fields import Date
from odoo.tools import (
    date_utils,
    float_compare,
    float_is_zero,
    float_repr,
    format_amount,
    format_date,
    formatLang,
    get_lang,
)


class GeneralLedgerReport(models.AbstractModel):
    _name = "report.account_cn.general_ledger"
    _inherit = "account_cn.report.abstract"
    _description = "General Ledger"

    @api.model
    def _get_report_values(self, docids, data=None):
        initial_balance_data = self._get_initial_balance_data(
            data["company_ids"],
            data["accounting_book_ids"],
            data["account_code"],
            data["exact_match"],
            data["date_from"],
            data["posted_only"],
            data["voucher_type_ids"],
            data["tag_ids"],
        )
        period_amount_data = self._get_period_amount_data(
            data["company_ids"],
            data["accounting_book_ids"],
            data["account_code"],
            data["exact_match"],
            data["date_from"],
            data["date_to"],
            data["posted_only"],
            data["voucher_type_ids"],
            data["tag_ids"],
        )
        general_ledger = self._generate_general_ledger(
            data,
            initial_balance_data,
            period_amount_data,
        )
        return {
            "data": data,
            "general_ledger": general_ledger,
        }

    def _get_initial_balance_data(
        self,
        company_ids,
        accounting_book_ids,
        account_code,
        exact_match,
        initial_date,
        posted_only,
        voucher_type_ids,
        tag_ids,
    ):
        domain = [
            ("company_id", "in", company_ids),
            ("accounting_book_id", "in", accounting_book_ids),
            ("date", "<=", self._last_year_end(Date.to_date(initial_date))),
        ]
        if exact_match:
            domain += [("account_id.code", "=", account_code)]
        else:
            domain += [("account_id.code", "=like", account_code + "%")]
        if posted_only:
            domain += [("voucher_state", "=", "posted")]
        if voucher_type_ids:
            domain += [("voucher_type_id", "in", voucher_type_ids)]
        if tag_ids:
            domain += [("tag_ids", "in", tag_ids)]

        fields = [
            "company_id",
            "debit:sum",
            "credit:sum",
        ]
        groupby = [
            "company_id",
        ]
        data = self.env["account.cn.voucher.line"].read_group(
            domain=domain,
            fields=fields,
            groupby=groupby,
            lazy=False,
        )
        return data

    def _get_period_amount_data(
        self,
        company_ids,
        accounting_book_ids,
        account_code,
        exact_match,
        date_from,
        date_to,
        posted_only,
        voucher_type_ids,
        tag_ids,
    ):
        domain = [
            ("company_id", "in", company_ids),
            ("accounting_book_id", "in", accounting_book_ids),
            ("date", ">", self._last_year_end(Date.to_date(date_from))),
            ("date", "<=", date_to),
        ]
        if exact_match:
            domain += [("account_id.code", "=", account_code)]
        else:
            domain += [("account_id.code", "=like", account_code + "%")]
        if posted_only:
            domain += [("voucher_state", "=", "posted")]
        if voucher_type_ids:
            domain += [("voucher_type_id", "in", voucher_type_ids)]
        if tag_ids:
            domain += [("tag_ids", "in", tag_ids)]

        fields = [
            "date",
            "date",
            "debit:sum",
            "credit:sum",
        ]
        groupby = [
            "date:year",
            "date:month",
        ]
        orderby = "date:year ASC, date:month ASC"
        data = self.env["account.cn.voucher.line"].read_group(
            domain=domain,
            fields=fields,
            groupby=groupby,
            orderby=orderby,
            lazy=False,
        )
        return list(map(self._convert_date_month_to_object, data))

    def _generate_general_ledger(
        self,
        data,
        initial_balance_data,
        period_amount_data,
    ):
        general_ledger = []
        initial_balance = {
            "date": self._this_year_start(Date.to_date(data["date_from"])),
            "summary": _("The year initial balance"),
            "debit": 0.0,
            "credit": 0.0,
            "orient": False,
            "balance": 0.0,
        }

        if initial_balance_data:
            for ib in initial_balance_data:
                initial_balance["balance"] += ib["debit"] - ib["credit"]
        general_ledger += [dict(initial_balance)]

        if period_amount_data:
            date_years = set()
            date_years.add(period_amount_data[0]["date:year"])
            total_month = {
                "date": None,
                "summary": _("The month total"),
                "debit": 0.0,
                "credit": 0.0,
                "orient": False,
                "balance": initial_balance["balance"],
            }
            total_year = {
                "date": None,
                "summary": _("The year total"),
                "debit": 0.0,
                "credit": 0.0,
                "orient": False,
                "balance": 0.0,
            }
            for pa in period_amount_data:
                if pa["date:year"] in date_years:
                    total_month["date"] = self._this_month_end(pa["date:month"])
                    total_month["debit"] = pa["debit"]
                    total_month["credit"] = pa["credit"]
                    total_month["balance"] = (
                        total_month["balance"] + pa["debit"] - pa["credit"]
                    )
                    general_ledger += [dict(total_month)]
                    total_year["date"] = total_month["date"]
                    total_year["debit"] += total_month["debit"]
                    total_year["credit"] += total_month["credit"]
                    total_year["balance"] = total_month["balance"]
                    initial_balance["balance"] = total_month["balance"]
                    general_ledger += [dict(total_year)]
                else:
                    date_years.add(pa["date:year"])
                    initial_balance["date"] = self._this_year_start(pa["date:month"])
                    general_ledger += [dict(initial_balance)]
                    total_month["date"] = self._this_month_end(pa["date:month"])
                    total_month["debit"] = pa["debit"]
                    total_month["credit"] = pa["credit"]
                    total_month["balance"] = (
                        total_month["balance"] + pa["debit"] - pa["credit"]
                    )
                    general_ledger += [dict(total_month)]
                    total_year["date"] = total_month["date"]
                    total_year["debit"] = total_month["debit"]
                    total_year["credit"] = total_month["credit"]
                    total_year["balance"] = total_month["balance"]
                    initial_balance["balance"] = total_month["balance"]
                    general_ledger += [dict(total_year)]

        return general_ledger
