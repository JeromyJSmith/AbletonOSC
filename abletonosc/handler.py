from ableton.v2.control_surface.component import Component
from typing import Optional, Tuple, Any
import logging
from .osc_server import OSCServer

class AbletonOSCHandler(Component):
    def __init__(self, manager):
        super().__init__()

        self.logger = logging.getLogger("abletonosc")
        self.manager = manager
        self.osc_server: OSCServer = self.manager.osc_server
        self.init_api()
        self.listener_functions = {}
        self.class_identifier = None

    def init_api(self):
        pass

    def clear_api(self):
        pass

    #--------------------------------------------------------------------------------
    # Generic callbacks
    #--------------------------------------------------------------------------------
    def _call_method(self, target, method, params: Optional[Tuple] = ()):
        self.logger.info(
            f"Calling method for {self.class_identifier}: {method} (params {str(params)})"
        )
        getattr(target, method)(*params)

    def _set_property(self, target, prop, params: Tuple) -> None:
        self.logger.info(
            f"Setting property for {self.class_identifier}: {prop} (new value {params[0]})"
        )
        setattr(target, prop, params[0])

    def _get_property(self, target, prop, params: Optional[Tuple] = ()) -> Tuple[Any]:
        value = getattr(target, prop)
        self.logger.info(
            f"Getting property for {self.class_identifier}: {prop} = {value}"
        )
        return value,

    def _start_listen(self, target, prop, params: Optional[Tuple] = ()) -> None:
        def property_changed_callback():
            value = getattr(target, prop)
            self.logger.info(f"Property {prop} changed: {value}")
            osc_address = f"/live/{self.class_identifier}/get/{prop}"
            self.osc_server.send(osc_address, (*params, value,))

        listener_key = (prop, tuple(params))
        if listener_key in self.listener_functions:
            self._stop_listen(target, prop, params)

        self.logger.info(
            f"Adding listener for {self.class_identifier} {str(params)}, property: {prop}"
        )
        add_listener_function_name = f"add_{prop}_listener"
        add_listener_function = getattr(target, add_listener_function_name)
        add_listener_function(property_changed_callback)
        self.listener_functions[listener_key] = property_changed_callback

    def _stop_listen(self, target, prop, params: Optional[Tuple[Any]] = ()) -> None:
        listener_key = (prop, tuple(params))
        if listener_key in self.listener_functions:
            self.logger.info(
                f"Removing listener for {self.class_identifier} {str(params)}, property {prop}"
            )
            listener_function = self.listener_functions[listener_key]
            remove_listener_function_name = f"remove_{prop}_listener"
            remove_listener_function = getattr(target, remove_listener_function_name)
            remove_listener_function(listener_function)
            del self.listener_functions[listener_key]
        else:
            self.logger.warning(
                f"No listener function found for property: {prop} ({str(params)})"
            )