from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    func,
)

from expensemgr.database.db import Base


class Connection(Base):
    __tablename__ = "connection"
    __table_args__ = (
        PrimaryKeyConstraint("connection_key", name="connection_pk"),
        ForeignKeyConstraint(
            ["user_key_1"], ["user_schema.user.user_key"], name="connection_fk01"
        ),
        ForeignKeyConstraint(
            ["user_key_2"], ["user_schema.user.user_key"], name="connection_fk02"
        ),
        {"schema": "user_schema"},
    )

    connection_key = Column(Integer, primary_key=True, index=True)
    user_key_1 = Column(
        Integer, ForeignKey("user_schema.user.user_key"), nullable=False
    )
    user_key_2 = Column(
        Integer, ForeignKey("user_schema.user.user_key"), nullable=False
    )
    user_consent_1 = Column(Boolean, default=False, nullable=False)
    user_consent_2 = Column(Boolean, default=False, nullable=False)
    meta_created_dttm = Column(DateTime, default=func.now(), nullable=False)
    meta_changed_dttm = Column(DateTime, default=func.now(), nullable=False)
    version_effective_dttm = Column(DateTime, default=func.now(), nullable=False)
    version_termination_dttm = Column(DateTime, default=None, nullable=True)
    delete_ind = Column(Boolean, default=False, nullable=False)
    version_active_ind = Column(Boolean, default=True, nullable=False)
