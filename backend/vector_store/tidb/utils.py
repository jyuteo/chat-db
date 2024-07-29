from typing import Type


def convert_sqlalchemy_model_to_dataclass(model_instance, dataclass_type: Type) -> object:
    model_dict = {column.name: getattr(model_instance, column.name) for column in model_instance.__table__.columns}
    return dataclass_type(**model_dict)
