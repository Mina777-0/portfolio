import inspect
from schemas import RangeValidator
from typing import get_args




def get_obj_info(obj):
    annotation= inspect.get_annotations(obj)
    return annotation

def validate_pool_size(obj, instance) -> int:
    for _field_name, _field_type in get_obj_info(obj).items():
        if hasattr(_field_type, '__metadata__'):
            args= get_args(_field_type)

            base_arg= args[0]
            metadata= args[1:]

            for item in metadata:
                if isinstance(item, RangeValidator):
                    value= getattr(instance, _field_name)
                    item.validate_range(value)
                    print(f"Max_value: {item.max_value} | Value: {value}")
                    
                    return value

