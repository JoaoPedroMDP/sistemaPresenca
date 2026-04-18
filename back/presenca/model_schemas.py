

from datetime import date, datetime, time

from ninja import Schema

class UserSchema(Schema):
    id: int
    email: str

class MemberSchema(Schema):
    id: int
    name: str
    birthday: date
    user: UserSchema

class CheckinSchema(Schema):
    member: MemberSchema
    date: datetime

class CodeSchema(Schema):
    code: str
    used: bool
    event_id: int

class ScoreboardSchema(Schema):
    name: str

class ScoreSchema(Schema):
    board_id: int
    member_id: int
    points: float

class TimeScoreRulesSchema(Schema):
    event_id: int
    start_time: time
    end_time: time
    points: float

