from sqlalchemy import insert, select, and_, or_, update, literal, case, exists
from datetime import datetime, timezone

from expensemgr.database.db import db_dependency
from expensemgr.services.users import user_dependency
from expensemgr.schemas.connection import ConnectionBase
from expensemgr.database.models.connection import Connection
from expensemgr.utils.constants import ConnectionConsent, VersionActiveInd


class CreateConnectionException(Exception):
    pass


class ConnectionService:
    def __init__(self, db: db_dependency, user: user_dependency):
        self.db = db
        self.user = user

    def get_connection_status(self, connection: ConnectionBase):
        pass

    def create_connection(self, connection: ConnectionBase):
        engine = self.db.get_engine()
        user_key = self.user.get("user_key")

        if connection.user_key == user_key:
            raise CreateConnectionException("Are you not your friend already?")

        with engine.begin() as conn:
            query = select(
                case(
                    (
                        exists(
                            select(literal(1)).where(
                                Connection.user_key_1 == user_key,
                                Connection.user_key_2 == connection.user_key,
                                Connection.user_consent_1
                                == ConnectionConsent.YES.value,
                                Connection.user_consent_2 == ConnectionConsent.NO.value,
                            )
                        ),
                        True,
                    ),
                    else_=False,
                )
            )
            if conn.execute(query).scalar():
                raise CreateConnectionException("You have already sent a request!")

            query = select(
                case(
                    (
                        exists(
                            select(literal(1)).where(
                                or_(
                                    and_(
                                        Connection.user_key_1 == user_key,
                                        Connection.user_key_2 == connection.user_key,
                                        Connection.user_consent_1
                                        == ConnectionConsent.YES.value,
                                        Connection.user_consent_2
                                        == ConnectionConsent.YES.value,
                                    ),
                                    and_(
                                        Connection.user_key_1 == connection.user_key,
                                        Connection.user_key_2 == user_key,
                                        Connection.user_consent_1
                                        == ConnectionConsent.YES.value,
                                        Connection.user_consent_2
                                        == ConnectionConsent.YES.value,
                                    ),
                                )
                            )
                        ),
                        True,
                    ),
                    else_=False,
                )
            )
            if conn.execute(query).scalar():
                raise CreateConnectionException("You are already a connection!")

            query = select(
                case(
                    (
                        exists(
                            select(literal(1)).where(
                                Connection.user_key_1 == connection.user_key,
                                Connection.user_key_2 == user_key,
                                Connection.user_consent_1
                                == ConnectionConsent.YES.value,
                                Connection.user_consent_2 == ConnectionConsent.NO.value,
                            )
                        ),
                        True,
                    ),
                    else_=False,
                )
            )
            if conn.execute(query).scalar():
                now = datetime.now(timezone.utc)
                query = (
                    update(Connection)
                    .where(
                        Connection.user_key_1 == connection.user_key,
                        Connection.user_key_2 == user_key,
                        Connection.user_consent_1 == ConnectionConsent.YES.value,
                        Connection.user_consent_2 == ConnectionConsent.NO.value,
                    )
                    .values(
                        meta_changed_dttm=now,
                        version_termination_dttm=now,
                        version_active_ind=VersionActiveInd.INACTIVE.value,
                    )
                )
                conn.execute(query)
                query = insert(Connection).values(
                    user_key_1=connection.user_key,
                    user_key_2=user_key,
                    user_consent_1=ConnectionConsent.YES.value,
                    user_consent_2=ConnectionConsent.YES.value,
                    meta_created_dttm=now,
                    version_effective_dttm=now,
                )
                conn.execute(query)
                return {"detail": "Accepted a pending connection!"}

            query = insert(Connection).values(
                user_key_1=user_key,
                user_key_2=connection.user_key,
                user_consent_1=ConnectionConsent.YES.value,
            )

            conn.execute(query)
            return {"detail": "Sent a connection request!"}
