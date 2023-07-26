import calendar
import datetime

from odoo import api, fields, models, _
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


class AccountBalanceReport(models.AbstractModel):
    _name = "report.account_cn.account_balance"

    @api.model
    def _get_report_values(self, docids, data=None):
        print("22222222222222222222222222222222222222222222222")
        print(data)
        if data["account_ids"]:
            accounts = self.env["account.account"].browse(data["account_ids"])
        else:
            accounts = self.env["account.account"].search([])
        print("22222222222222222222222222222222222222222222222")
        print(accounts)
        max_account_code_length = data["max_account_code_length"]
        account_codes = [
            account.code
            for account in accounts
            if len(account.code) <= max_account_code_length
        ]
        initial_balance_data = self._get_initial_balance_data(
            data["company_ids"],
            data["accounting_book_ids"],
            data["account_code"],
            data["exact_match"],
            data["date_from"],
            data["posted_only"],
            data["distinguish_partner"],
            data["partner_ids"],
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
            data["distinguish_partner"],
            data["partner_ids"],
            data["voucher_type_ids"],
            data["tag_ids"],
        )
        subsidiary_ledger = self._generate_subsidiary_ledger(
            data,
            initial_balance_data,
            period_amount_data,
        )
        return {
            "data": data,
            "subsidiary_ledger": subsidiary_ledger,
        }

    def _get_initial_balance_data(
        self,
        company_ids,
        accounting_book_ids,
        account_code,
        exact_match,
        initial_date,
        posted_only,
        distinguish_partner,
        partner_ids,
        voucher_type_ids,
        tag_ids,
    ):
        domain = [
            ("company_id", "in", company_ids),
            ("accounting_book_id", "in", accounting_book_ids),
            ("date", "<", initial_date),
        ]
        fields = []
        groupby = []
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

        if distinguish_partner:
            domain += [("partner_id", "in", partner_ids)]
            fields += ["partner_id"]
            groupby += ["partner_id"]
        fields += [
            "company_id",
            "debit:sum",
            "credit:sum",
        ]
        groupby += [
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
        distinguish_partner,
        partner_ids,
        voucher_type_ids,
        tag_ids,
    ):
        domain = [
            ("company_id", "in", company_ids),
            ("accounting_book_id", "in", accounting_book_ids),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
        ]
        fields = []
        groupby = []
        orderby = ""
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

        if distinguish_partner:
            domain += [("partner_id", "in", partner_ids)]
            fields += ["partner_id"]
            groupby += ["partner_id"]
            orderby += "partner_id, "
        fields += [
            "debit:sum",
            "credit:sum",
        ]
        groupby += [
            "company_id",
        ]
        data = self.env["account.cn.voucher.line"].read_group(
            domain=domain,
            fields=fields,
            groupby=groupby,
            orderby=orderby,
            lazy=False,
        )
        return data

    def _generate_subsidiary_ledger(
        self,
        data,
        initial_balance_data,
        period_amount_data,
    ):
        if data["distinguish_partner"]:
            subsidiary_ledger = []
            for partner_id in data["partner_ids"]:
                initial_balance_data_filtered = list(
                    filter(
                        lambda r: r["partner_id"][0] == partner_id,
                        initial_balance_data,
                    )
                )
                period_amount_data_filtered = list(
                    filter(
                        lambda r: r["partner_id"][0] == partner_id,
                        period_amount_data,
                    )
                )
                partner_name = self.env["res.partner"].browse([partner_id]).name
                addition = {
                    "partner_id": partner_id,
                    "partner_name": partner_name,
                }
                subsidiary_ledger += self._make_subsidiary_ledger(
                    data,
                    initial_balance_data_filtered,
                    period_amount_data_filtered,
                    addition,
                )
            return subsidiary_ledger
        else:
            return self._make_subsidiary_ledger(
                data, initial_balance_data, period_amount_data
            )

    def _make_subsidiary_ledger(
        self,
        data,
        initial_balance_data,
        period_amount_data,
        addition=False,
    ):
        subsidiary_ledger = []
        initial_balance = {
            "date": data["date_from"],
            "voucher_id": None,
            "voucher_word_number": None,
            "summary": _("Initial balance"),
            "debit": 0.0,
            "credit": 0.0,
            "orient": False,
            "balance": 0.0,
        }
        if addition:
            initial_balance.update(addition)

        if initial_balance_data:
            for ib in initial_balance_data:
                initial_balance["debit"] += ib["debit"]
                initial_balance["credit"] += ib["credit"]

            initial_balance["balance"] = (
                initial_balance["debit"] - initial_balance["credit"]
            )
        subsidiary_ledger += [initial_balance]

        if period_amount_data:
            date_years = set()
            date_months = set()
            date_years.add(period_amount_data[0]["date:year"])
            date_months.add(period_amount_data[0]["date:month"])
            total_month = {
                "date": None,
                "voucher_id": None,
                "voucher_word_number": None,
                "summary": _("The month total"),
                "debit": 0.0,
                "credit": 0.0,
                "orient": False,
                "balance": initial_balance["balance"],
            }
            total_year = {
                "date": None,
                "voucher_id": None,
                "voucher_word_number": None,
                "summary": _("The year total"),
                "debit": 0.0,
                "credit": 0.0,
                "orient": False,
                "balance": 0.0,
            }
            if addition:
                total_month.update(addition)
                total_year.update(addition)
            for pa in period_amount_data:
                item = {
                    "date": pa["date:day"],
                    "voucher_id": pa["voucher_id"][0],
                    "voucher_word_number": pa["voucher_word"][1]
                    + "-"
                    + str(pa["voucher_number"]),
                    "summary": pa["summary"],
                    "debit": pa["debit"],
                    "credit": pa["credit"],
                    "orient": False,
                    "balance": 0.0,
                }
                if addition:
                    item.update(addition)
                if pa["date:month"] in date_months:
                    total_month["debit"] += item["debit"]
                    total_month["credit"] += item["credit"]
                    total_month["balance"] = (
                        total_month["balance"] + item["debit"] - item["credit"]
                    )
                    item["balance"] = total_month["balance"]
                    subsidiary_ledger += [item]
                elif pa["date:year"] in date_years:
                    date_months.add(pa["date:month"])
                    total_month["date"] = self._last_month_end(pa["date:day"])
                    subsidiary_ledger += [dict(total_month)]
                    total_year["date"] = total_month["date"]
                    total_year["debit"] += total_month["debit"]
                    total_year["credit"] += total_month["credit"]
                    total_year["balance"] = total_month["balance"]
                    subsidiary_ledger += [dict(total_year)]
                    total_month["debit"] = item["debit"]
                    total_month["credit"] = item["credit"]
                    total_month["balance"] = (
                        total_month["balance"] + item["debit"] - item["credit"]
                    )
                    item["balance"] = total_month["balance"]
                    subsidiary_ledger += [item]
                else:
                    date_months.add(pa["date:month"])
                    date_years.add(pa["date:year"])
                    total_month["date"] = self._last_year_end(pa["date:day"])
                    subsidiary_ledger += [dict(total_month)]
                    total_year["date"] = total_month["date"]
                    total_year["debit"] += total_month["debit"]
                    total_year["credit"] += total_month["credit"]
                    total_year["balance"] = total_month["balance"]
                    subsidiary_ledger += [dict(total_year)]
                    total_month["debit"] = item["debit"]
                    total_month["credit"] = item["credit"]
                    total_month["balance"] = (
                        total_month["balance"] + item["debit"] - item["credit"]
                    )
                    item["balance"] = total_month["balance"]
                    subsidiary_ledger += [item]
                    total_year["debit"] = 0.0
                    total_year["credit"] = 0.0

            total_month["date"] = self._this_month_end(
                period_amount_data[-1]["date:day"]
            )
            subsidiary_ledger += [total_month]
            total_year["date"] = total_month["date"]
            total_year["debit"] += total_month["debit"]
            total_year["credit"] += total_month["credit"]
            total_year["balance"] = total_month["balance"]
            subsidiary_ledger += [total_year]

        return subsidiary_ledger

    def _last_month_end(self, date):
        return date_utils.end_of(date_utils.subtract(date, months=1), "month")

    def _last_year_end(self, date):
        return date_utils.end_of(date_utils.subtract(date, years=1), "year")

    def _this_month_end(self, date):
        return date_utils.end_of(date, "month")

    def _convert_date_day_to_object(self, data):
        lang = self.env.lang
        if lang == "en_US":
            data["date:day"] = self._convert_date_day_to_object_en_US(data["date:day"])
            return data
        elif lang == "zh_CN":
            data["date:day"] = self._convert_date_day_to_object_zh_CN(data["date:day"])
            return data
        else:
            return data

    def _convert_date_day_to_object_en_US(self, date_day):
        return fields.Date.to_date(datetime.datetime.strptime(date_day, "%d %b %Y"))

    def _convert_date_day_to_object_zh_CN(self, date_day):
        year = date_day[-4:]
        month = date_day[3:-6]
        day = date_day[0:2]
        return datetime.date(int(year), int(month), int(day))
