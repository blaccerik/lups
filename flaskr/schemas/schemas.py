from marshmallow import Schema, fields


class ChatResponseSchema(Schema):
    est_output = fields.Str()
    eng_output = fields.Str()
