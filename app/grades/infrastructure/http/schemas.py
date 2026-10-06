from app.shared.http.schemas import BaseSchema


class GradeResponse(BaseSchema):
    subject: str
    value: int


class GradesPageResponse(BaseSchema):
    results: list[GradeResponse]
