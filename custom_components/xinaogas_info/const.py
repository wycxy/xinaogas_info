"""Constants for the Xinao Gas Info integration."""

DOMAIN = "xinaogas_info"
NAME = "新奥燃气信息"

# 计费标准选项
GAS_BILLING_YEAR_阶梯 = "gas_year_ladder"
GAS_BILLING_MONTH_阶梯 = "gas_month_ladder"
GAS_BILLING_平均单价 = "gas_average"

GAS_BILLING_OPTIONS = [
    GAS_BILLING_YEAR_阶梯,
    GAS_BILLING_MONTH_阶梯,
    GAS_BILLING_平均单价,
]

GAS_BILLING_NAMES = {
    GAS_BILLING_YEAR_阶梯: "年阶梯气价",
    GAS_BILLING_MONTH_阶梯: "月阶梯气价",
    GAS_BILLING_平均单价: "平均气价",
}

# 配置项
CONF_CONSUMER_NUMBER = "consumer_number"
CONF_GAS_BILLING_STANDARD = "gas_billing_standard"
CONF_GAS_LADDER_LEVEL_1 = "gas_ladder_level_1"
CONF_GAS_LADDER_LEVEL_2 = "gas_ladder_level_2"
CONF_GAS_LADDER_PRICE_1 = "gas_ladder_price_1"
CONF_GAS_LADDER_PRICE_2 = "gas_ladder_price_2"
CONF_GAS_LADDER_PRICE_3 = "gas_ladder_price_3"
CONF_GAS_YEAR_LADDER_START = "gas_year_ladder_start"
CONF_GAS_AVERAGE_PRICE = "gas_average_price"
