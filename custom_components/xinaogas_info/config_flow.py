"""Config flow for Xinao Gas Info integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN, NAME,
    GAS_BILLING_OPTIONS, GAS_BILLING_NAMES,
    GAS_BILLING_YEAR_阶梯, GAS_BILLING_MONTH_阶梯, GAS_BILLING_平均单价,
    CONF_CONSUMER_NUMBER,
    CONF_GAS_BILLING_STANDARD,
    CONF_GAS_LADDER_LEVEL_1, CONF_GAS_LADDER_LEVEL_2,
    CONF_GAS_LADDER_PRICE_1, CONF_GAS_LADDER_PRICE_2, CONF_GAS_LADDER_PRICE_3,
    CONF_GAS_YEAR_LADDER_START, CONF_GAS_AVERAGE_PRICE,
)

_LOGGER = logging.getLogger(__name__)


class XinaoGasInfoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Xinao Gas Info."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get the options flow for this handler."""
        return XinaoGasInfoOptionsFlowHandler(config_entry)

    def __init__(self):
        self._data = {}

    async def async_step_user(self, user_input=None):
        return await self.async_step_gas_consumer(user_input)

    async def async_step_gas_consumer(self, user_input=None):
        """选择燃气户号."""
        errors = {}

        if user_input is not None and not errors:
            self._data[CONF_CONSUMER_NUMBER] = user_input[CONF_CONSUMER_NUMBER]
            return await self.async_step_gas_billing()

        gas_accounts = self._get_gas_accounts()
        if not gas_accounts:
            errors["base"] = "gas_not_configured"

        consumer_options = {acc["payment_no"]: acc["label"] for acc in gas_accounts}

        return self.async_show_form(
            step_id="gas_consumer",
            data_schema=vol.Schema({
                vol.Required(CONF_CONSUMER_NUMBER): vol.In(consumer_options),
            }) if consumer_options else vol.Schema({}),
            errors=errors,
        )

    async def async_step_gas_billing(self, user_input=None):
        """选择燃气计费标准."""
        errors = {}

        if user_input is not None:
            self._data[CONF_GAS_BILLING_STANDARD] = user_input[CONF_GAS_BILLING_STANDARD]
            schema = self._get_gas_billing_schema(user_input[CONF_GAS_BILLING_STANDARD], self._data)
            return self.async_show_form(
                step_id="gas_billing_config",
                data_schema=vol.Schema(schema),
                errors=errors,
                description_placeholders={
                    "standard": GAS_BILLING_NAMES.get(user_input[CONF_GAS_BILLING_STANDARD], ""),
                },
            )

        gas_billing_options = {k: GAS_BILLING_NAMES[k] for k in GAS_BILLING_OPTIONS}

        return self.async_show_form(
            step_id="gas_billing",
            data_schema=vol.Schema({
                vol.Required(CONF_GAS_BILLING_STANDARD): vol.In(gas_billing_options),
            }),
            errors=errors,
        )

    async def async_step_gas_billing_config(self, user_input=None):
        """燃气计费标准配置."""
        errors = {}
        current_standard = self._data.get(CONF_GAS_BILLING_STANDARD)

        if user_input is not None:
            for key, value in user_input.items():
                self._data[key] = value
            title = f"新奥燃气 - {self._data.get(CONF_CONSUMER_NUMBER)}"
            return self.async_create_entry(title=title, data=self._data)

        schema = self._get_gas_billing_schema(current_standard, self._data)

        return self.async_show_form(
            step_id="gas_billing_config",
            data_schema=vol.Schema(schema),
            errors=errors,
            description_placeholders={
                "standard": GAS_BILLING_NAMES.get(current_standard, ""),
            },
            last_step=True,
        )

    def _get_gas_accounts(self):
        """从 xinaogas 集成获取可用的燃气账户列表。"""
        accounts = []
        xinaogas_domain = self.hass.data.get("xinaogas", {})
        coordinators = xinaogas_domain.get("coordinators", {})
        for coordinator in coordinators.values():
            data = coordinator.data or {}
            payment_no = str(data.get("payment_no") or "").strip()
            if not payment_no:
                continue
            user_name = data.get("user_name") or data.get("family_account_name") or ""
            address = data.get("address") or ""
            label = f"{payment_no}"
            if user_name:
                label += f"（{user_name}）"
            if address:
                label += f" - {address}"
            accounts.append({"payment_no": payment_no, "label": label})
        # 兼容旧式存储
        if not accounts:
            for key, value in xinaogas_domain.items():
                if key in ("token_manager", "coordinators"):
                    continue
                if hasattr(value, "data") and isinstance(value.data, dict):
                    data = value.data
                    payment_no = str(data.get("payment_no") or "").strip()
                    if payment_no:
                        user_name = data.get("user_name") or ""
                        label = f"{payment_no}"
                        if user_name:
                            label += f"（{user_name}）"
                        accounts.append({"payment_no": payment_no, "label": label})
        return accounts

    def _get_gas_billing_schema(self, current_standard, existing_data=None):
        """获取燃气计费标准表单配置。"""
        if existing_data is None:
            existing_data = {}

        schema = {}

        if current_standard == GAS_BILLING_YEAR_阶梯:
            schema = {
                vol.Required(CONF_GAS_YEAR_LADDER_START, default=existing_data.get(CONF_GAS_YEAR_LADDER_START, "0101")): cv.string,
                vol.Required(CONF_GAS_LADDER_LEVEL_1, default=existing_data.get(CONF_GAS_LADDER_LEVEL_1, 600)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_LEVEL_2, default=existing_data.get(CONF_GAS_LADDER_LEVEL_2, 600)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_PRICE_1, default=existing_data.get(CONF_GAS_LADDER_PRICE_1, 2.66)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_PRICE_2, default=existing_data.get(CONF_GAS_LADDER_PRICE_2, 3.46)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_PRICE_3, default=existing_data.get(CONF_GAS_LADDER_PRICE_3, 3.46)): cv.positive_float,
            }
        elif current_standard == GAS_BILLING_MONTH_阶梯:
            schema = {
                vol.Required(CONF_GAS_LADDER_LEVEL_1, default=existing_data.get(CONF_GAS_LADDER_LEVEL_1, 50)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_LEVEL_2, default=existing_data.get(CONF_GAS_LADDER_LEVEL_2, 50)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_PRICE_1, default=existing_data.get(CONF_GAS_LADDER_PRICE_1, 2.66)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_PRICE_2, default=existing_data.get(CONF_GAS_LADDER_PRICE_2, 3.46)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_PRICE_3, default=existing_data.get(CONF_GAS_LADDER_PRICE_3, 3.46)): cv.positive_float,
            }
        elif current_standard == GAS_BILLING_平均单价:
            schema = {
                vol.Required(CONF_GAS_AVERAGE_PRICE, default=existing_data.get(CONF_GAS_AVERAGE_PRICE, 2.66)): cv.positive_float,
            }

        return schema


class XinaoGasInfoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Xinao Gas Info."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self._config_entry = config_entry
        self._data = dict(config_entry.data)

    async def async_step_init(self, user_input=None):
        return await self.async_step_gas_consumer(user_input)

    async def async_step_gas_consumer(self, user_input=None):
        errors = {}

        if user_input is not None and not errors:
            self._data[CONF_CONSUMER_NUMBER] = user_input[CONF_CONSUMER_NUMBER]
            return await self.async_step_gas_billing()

        gas_accounts = self._get_gas_accounts()
        if not gas_accounts:
            errors["base"] = "gas_not_configured"

        consumer_options = {acc["payment_no"]: acc["label"] for acc in gas_accounts}
        current_consumer = self._data.get(CONF_CONSUMER_NUMBER)

        return self.async_show_form(
            step_id="gas_consumer",
            data_schema=vol.Schema({
                vol.Required(CONF_CONSUMER_NUMBER, default=current_consumer): vol.In(consumer_options),
            }) if consumer_options else vol.Schema({}),
            errors=errors,
        )

    async def async_step_gas_billing(self, user_input=None):
        errors = {}

        if user_input is not None:
            self._data[CONF_GAS_BILLING_STANDARD] = user_input[CONF_GAS_BILLING_STANDARD]
            schema = self._get_gas_billing_schema(user_input[CONF_GAS_BILLING_STANDARD], self._data)
            return self.async_show_form(
                step_id="gas_billing_config",
                data_schema=vol.Schema(schema),
                errors=errors,
                description_placeholders={
                    "standard": GAS_BILLING_NAMES.get(user_input[CONF_GAS_BILLING_STANDARD], ""),
                },
            )

        gas_billing_options = {k: GAS_BILLING_NAMES[k] for k in GAS_BILLING_OPTIONS}
        current_standard = self._data.get(CONF_GAS_BILLING_STANDARD)

        return self.async_show_form(
            step_id="gas_billing",
            data_schema=vol.Schema({
                vol.Required(CONF_GAS_BILLING_STANDARD, default=current_standard): vol.In(gas_billing_options),
            }),
            errors=errors,
        )

    async def async_step_gas_billing_config(self, user_input=None):
        errors = {}
        current_standard = self._data.get(CONF_GAS_BILLING_STANDARD)

        if user_input is not None:
            for key, value in user_input.items():
                self._data[key] = value
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data=self._data,
                options=self._config_entry.options,
            )
            await self.hass.config_entries.async_reload(self._config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        schema = self._get_gas_billing_schema(current_standard, self._data)

        return self.async_show_form(
            step_id="gas_billing_config",
            data_schema=vol.Schema(schema),
            errors=errors,
            description_placeholders={
                "standard": GAS_BILLING_NAMES.get(current_standard, ""),
            },
            last_step=True,
        )

    def _get_gas_accounts(self):
        accounts = []
        xinaogas_domain = self.hass.data.get("xinaogas", {})
        coordinators = xinaogas_domain.get("coordinators", {})
        for coordinator in coordinators.values():
            data = coordinator.data or {}
            payment_no = str(data.get("payment_no") or "").strip()
            if not payment_no:
                continue
            user_name = data.get("user_name") or data.get("family_account_name") or ""
            address = data.get("address") or ""
            label = f"{payment_no}"
            if user_name:
                label += f"（{user_name}）"
            if address:
                label += f" - {address}"
            accounts.append({"payment_no": payment_no, "label": label})
        if not accounts:
            for key, value in xinaogas_domain.items():
                if key in ("token_manager", "coordinators"):
                    continue
                if hasattr(value, "data") and isinstance(value.data, dict):
                    data = value.data
                    payment_no = str(data.get("payment_no") or "").strip()
                    if payment_no:
                        user_name = data.get("user_name") or ""
                        label = f"{payment_no}"
                        if user_name:
                            label += f"（{user_name}）"
                        accounts.append({"payment_no": payment_no, "label": label})
        return accounts

    def _get_gas_billing_schema(self, current_standard, existing_data=None):
        if existing_data is None:
            existing_data = {}

        schema = {}

        if current_standard == GAS_BILLING_YEAR_阶梯:
            schema = {
                vol.Required(CONF_GAS_YEAR_LADDER_START, default=existing_data.get(CONF_GAS_YEAR_LADDER_START, "0101")): cv.string,
                vol.Required(CONF_GAS_LADDER_LEVEL_1, default=existing_data.get(CONF_GAS_LADDER_LEVEL_1, 600)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_LEVEL_2, default=existing_data.get(CONF_GAS_LADDER_LEVEL_2, 600)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_PRICE_1, default=existing_data.get(CONF_GAS_LADDER_PRICE_1, 2.66)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_PRICE_2, default=existing_data.get(CONF_GAS_LADDER_PRICE_2, 3.46)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_PRICE_3, default=existing_data.get(CONF_GAS_LADDER_PRICE_3, 3.46)): cv.positive_float,
            }
        elif current_standard == GAS_BILLING_MONTH_阶梯:
            schema = {
                vol.Required(CONF_GAS_LADDER_LEVEL_1, default=existing_data.get(CONF_GAS_LADDER_LEVEL_1, 50)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_LEVEL_2, default=existing_data.get(CONF_GAS_LADDER_LEVEL_2, 50)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_PRICE_1, default=existing_data.get(CONF_GAS_LADDER_PRICE_1, 2.66)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_PRICE_2, default=existing_data.get(CONF_GAS_LADDER_PRICE_2, 3.46)): cv.positive_float,
                vol.Required(CONF_GAS_LADDER_PRICE_3, default=existing_data.get(CONF_GAS_LADDER_PRICE_3, 3.46)): cv.positive_float,
            }
        elif current_standard == GAS_BILLING_平均单价:
            schema = {
                vol.Required(CONF_GAS_AVERAGE_PRICE, default=existing_data.get(CONF_GAS_AVERAGE_PRICE, 2.66)): cv.positive_float,
            }

        return schema


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
