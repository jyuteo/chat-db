from marshmallow import Schema, fields, ValidationError

from vector_store import VectorStoreType
from llm import LLMType
from db_client import DBType


def validate_enum(enum_class):
    def _validate(value):
        if value not in enum_class._value2member_map_:
            raise ValidationError(
                f"Invalid value '{value}', must be one of {list(enum_class._value2member_map_.keys())}."
            )

    return _validate


class LLMConfigSchema(Schema):
    api_key = fields.String(required=True)


class LLMSchema(Schema):
    type = fields.String(required=True, validate=validate_enum(LLMType))
    config = fields.Nested(LLMConfigSchema, required=True)


class DBConfigSchema(Schema):
    host = fields.String(required=True)
    user = fields.String(required=True)
    password = fields.String(required=True)
    database = fields.String(required=True)
    port = fields.Integer(required=False, missing=3306)


class DBSchema(Schema):
    type = fields.String(required=True, validate=validate_enum(DBType))
    config = fields.Nested(DBConfigSchema, required=True)


class CreateChatSessionSchema(Schema):
    llm = fields.Nested(LLMSchema, required=True)
    db = fields.Nested(DBSchema, required=True)


class SendMessageSchema(Schema):
    question = fields.String(required=True)


class DBTableInfoSchema(Schema):
    database_name = fields.String(required=True)
    table_name = fields.String(required=True)
    table_schema = fields.String(required=True)


class QuestionSQLSchema(Schema):
    database_name = fields.String(required=False)
    table_name = fields.String(required=False)
    question = fields.String(required=True)
    sql = fields.String(required=True)
    metadatas = fields.Dict(required=False)


class AddDBTableInfoSchema(Schema):
    db_type = fields.String(required=True)
    embedding_model_type = fields.String(required=True)
    vector_store_type = fields.String(required=True)
    data = fields.List(fields.Nested(DBTableInfoSchema), required=True)


class AddQuestionSQLPairsSchema(Schema):
    db_type = fields.String(required=True)
    embedding_model_type = fields.String(required=True)
    vector_store_type = fields.String(required=True)
    data = fields.List(fields.Nested(QuestionSQLSchema), required=True)
