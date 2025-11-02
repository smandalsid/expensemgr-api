from expensemgr.database.db import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, PrimaryKeyConstraint

# Models for user_schema tables

class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        PrimaryKeyConstraint("user_key", name="user_pk"),
        {"schema": "user_schema"},
    )
    
    user_key = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    is_admin = Column(Boolean, server_default='FALSE')
    last_login = Column(DateTime, default=func.now())
    meta_changed_dttm = Column(DateTime, default=func.now())
    meta_changed_by = Column(Integer, nullable=False)
    user_active_ind = Column(Boolean, server_default='TRUE')