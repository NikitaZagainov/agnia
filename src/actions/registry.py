from typing import Type, Any, Callable

from pydantic import BaseModel

from src.actions.exceptions import SystemNotFoundException, ActionNotFoundException


class ActionRegistry:
    def __init__(self):
        self._actions = {}

    def register_action(
            self,
            system_name: str,
            action_name: str,
            action_obj: Any,
            input_type: Type[BaseModel],
            output_type: Type[BaseModel],
            result_message_func: Callable | None = None
    ):
        if system_name not in self._actions:
            self._actions[system_name] = {}

        self._actions[system_name][action_name] = {
            'object': action_obj,
            'input_type': input_type,
            'output_type': output_type,
            'result_message_func': result_message_func
        }

    def get_action_object(self, system_name: str, action_name: str) -> Any:
        try:
            return self._actions[system_name][action_name]['object']
        except KeyError:
            if system_name not in self._actions:
                raise SystemNotFoundException(f"System '{system_name}' not found")
            raise ActionNotFoundException(f"Action '{action_name}' not found for system '{system_name}'")

    def get_input_type(self, system_name: str, action_name: str) -> Type[BaseModel]:
        try:
            return self._actions[system_name][action_name]['input_type']
        except KeyError:
            if system_name not in self._actions:
                raise SystemNotFoundException(f"System '{system_name}' not found")
            raise ActionNotFoundException(f"Action '{action_name}' not found for system '{system_name}'")

    def get_output_type(self, system_name: str, action_name: str) -> Type[BaseModel]:
        try:
            return self._actions[system_name][action_name]['output_type']
        except KeyError:
            if system_name not in self._actions:
                raise SystemNotFoundException(f"System '{system_name}' not found")
            raise ActionNotFoundException(f"Action '{action_name}' not found for system '{system_name}'")

    def get_result_message_former(self, system_name: str, action_name: str) -> Callable:
        try:
            return self._actions[system_name][action_name]['result_message_func']
        except KeyError:
            if system_name not in self._actions:
                raise SystemNotFoundException(f"System '{system_name}' not found")
            raise ActionNotFoundException(f"Action '{action_name}' not found for system '{system_name}'")


# Create a global action registry
action_registry = ActionRegistry()


def register_action(
        input_type: Type[BaseModel],
        output_type: Type[BaseModel],
        system_name: str = "General",
        action_name: str | None = None,
        result_message_func: Callable | None = None
):
    def decorator(action_obj: Any):
        nonlocal action_name
        if not action_name:
            action_name = getattr(action_obj, 'action_name', None)
        if not action_name:
            raise ValueError(
                f"Action object {action_obj.__name__ if hasattr(action_obj, '__name__') else action_obj} must have an 'action_name' attribute or 'action_name' must be provided."
            )

        action_registry.register_action(
            system_name,
            action_name,
            action_obj,
            input_type,
            output_type,
            result_message_func=result_message_func
        )
        return action_obj

    return decorator
