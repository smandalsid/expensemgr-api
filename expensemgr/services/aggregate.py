from sqlalchemy import select, case, func, or_, and_

from expensemgr.services.users import user_dependency
from expensemgr.database.db import db_dependency
from expensemgr.database.models.expense import ExpenseVer, Expense
from expensemgr.database.models.users import User
from expensemgr.utils.constants import VersionActiveInd, ExpenseStatus, DeleteInd
from expensemgr.schemas.aggregate import AggregateShareOut
from expensemgr.services.expense import ExpenseService

class AggregateException(Exception):
    pass

class AggregateService:
    def __init__(self, db: db_dependency, user: user_dependency):
        self.db = db
        self.user = user

    def get_aggregate(self) -> list[AggregateShareOut]:
        user_key = self.user.get("user_key")
        user_case = case(
            (ExpenseVer.primary_user_key == user_key, ExpenseVer.secondary_user_key),
            (ExpenseVer.secondary_user_key == user_key, ExpenseVer.primary_user_key),
        )
        expense_case = case(
            (ExpenseVer.primary_user_key == user_key, ExpenseVer.expense_share),
            (ExpenseVer.secondary_user_key == user_key, -(ExpenseVer.expense_share)),
        )

        query_cte = (
            select(
                user_case.label("user_key"), func.sum(expense_case).label("user_total")
            )
            .where(
                ExpenseVer.version_active_ind == VersionActiveInd.ACTIVE.value,
                ExpenseVer.expense_ver_status == ExpenseStatus.DUE.value,
                or_(
                    ExpenseVer.primary_user_key == user_key,
                    ExpenseVer.secondary_user_key == user_key,
                ),
            )
            .group_by(user_case)
            .cte("shares")
        )
        query = select(
            query_cte,
            User.first_name.label("first_name"),
            User.last_name.label("last_name"),
        ).join(User, User.user_key == query_cte.c.user_key)

        user_shares = self.db.fetch_records(query=query)
        aggregate_return = [
            AggregateShareOut(
                user_key=row.user_key,
                first_name=row.first_name,
                last_name=row.last_name,
                user_total=row.user_total,
            )
            for row in user_shares
        ]
        return aggregate_return

    def settle_aggregate(self, settle_with_user_key: int):
        try:
            engine = self.db.get_engine()
            user_key = self.user.get("user_key")
            with engine.begin() as conn:
                query = select(
                    ExpenseVer.expense_ver_key.label("expense_ver_key")
                ).join(
                    Expense,
                    Expense.expense_key == ExpenseVer.expense_key
                ).where(
                    Expense.delete_ind == DeleteInd.NO.value,
                    ExpenseVer.version_active_ind == VersionActiveInd.ACTIVE.value,
                    ExpenseVer.expense_ver_status == ExpenseStatus.DUE.value,
                    or_(
                        and_(
                            ExpenseVer.primary_user_key == user_key,
                            ExpenseVer.secondary_user_key == settle_with_user_key
                        ),
                        and_(
                            ExpenseVer.primary_user_key == settle_with_user_key,
                            ExpenseVer.secondary_user_key == user_key
                        )
                    ),

                )
                expense_ver_keys = self.db.fetch_records(query=query)

                for expense_ver_key in expense_ver_keys:
                    ExpenseService(db=self.db, user=self.user)._settle_expense_ver(conn=conn, expense_ver_key=expense_ver_key[0])
                return {'detail': 'Account successfully settled!'}
        except Exception as e:
            raise AggregateException(f"Couldn't settle your account due to {str(e)}")