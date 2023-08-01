import datetime

from odoo import models
from odoo.fields import Date
from odoo.tools import date_utils


class ReportAbstract(models.AbstractModel):
    _name = "account_cn.report.abstract"
    _description = "Report Abstract"

    def _last_month_end(self, date):
        return date_utils.end_of(date_utils.subtract(date, months=1), "month")

    def _last_year_end(self, date):
        return date_utils.end_of(date_utils.subtract(date, years=1), "year")

    def _this_month_end(self, date):
        return date_utils.end_of(date, "month")

    def _this_year_start(self, date):
        return date_utils.start_of(date, "year")

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
        return Date.to_date(datetime.datetime.strptime(date_day, "%d %b %Y"))

    def _convert_date_day_to_object_zh_CN(self, date_day):
        year = date_day[-4:]
        month = date_day[3:-6]
        day = date_day[0:2]
        return datetime.date(int(year), int(month), int(day))

    def _convert_date_month_to_object(self, data):
        lang = self.env.lang
        if lang == "en_US":
            data["date:month"] = self._convert_date_month_to_object_en_US(
                data["date:month"]
            )
            return data
        elif lang == "zh_CN":
            data["date:month"] = self._convert_date_month_to_object_zh_CN(
                data["date:month"]
            )
            return data
        else:
            return data

    def _convert_date_month_to_object_en_US(self, date_month):
        return Date.to_date(datetime.datetime.strptime("01 " + date_month, "%d %B %Y"))

    def _convert_date_month_to_object_zh_CN(self, date_month):
        MONTH = {
            "一月": 1,
            "二月": 2,
            "三月": 3,
            "四月": 4,
            "五月": 5,
            "六月": 6,
            "七月": 7,
            "八月": 8,
            "九月": 9,
            "十月": 10,
            "十一月": 11,
            "十二月": 12,
        }
        year = date_month[-4:]
        month = MONTH[date_month[0:-5]]
        return datetime.date(int(year), month, 1)
