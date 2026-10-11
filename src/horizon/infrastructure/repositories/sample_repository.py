from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from horizon.domain.sample_record import SampleRecord
from horizon.infrastructure.database import ImportedRecordModel
from horizon.infrastructure.importers.models import ImportedItem


class SqlAlchemySampleRecordRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_domain(model: ImportedRecordModel) -> SampleRecord:
        return SampleRecord(
            id=model.id,
            source_file=model.source_file,
            source_identifier=model.source_identifier,
            source_format=model.source_format,
            payload=model.payload,
            imported_at=model.imported_at,
        )

    def list_records(
        self,
        *,
        limit: int,
        source_file: str | None = None,
    ) -> list[SampleRecord]:
        statement = select(ImportedRecordModel).order_by(ImportedRecordModel.id).limit(limit)
        if source_file:
            statement = statement.where(ImportedRecordModel.source_file == source_file)
        models = self._session.scalars(statement).all()
        return [self._to_domain(model) for model in models]

    def get_record(self, record_id: int) -> SampleRecord | None:
        model = self._session.get(ImportedRecordModel, record_id)
        return self._to_domain(model) if model else None

    def add_items(self, items: list[ImportedItem]) -> int:
        models = [
            ImportedRecordModel(
                source_file=item.source_file,
                source_identifier=item.source_identifier,
                source_format=item.source_format,
                payload=item.payload,
            )
            for item in items
        ]
        self._session.add_all(models)
        self._session.commit()
        return len(models)

    def clear(self) -> None:
        self._session.execute(delete(ImportedRecordModel))
        self._session.commit()
