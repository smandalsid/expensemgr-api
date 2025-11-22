SELECT TOP (1000) [user_key]
      ,[email]
      ,[first_name]
      ,[last_name]
      ,[username]
      ,[password]
      ,[phone_number]
      ,[is_admin]
      ,[last_login]
      ,[meta_changed_dttm]
      ,[user_active_ind]
  FROM [ExpenseMgr].[user_schema].[user]

update [ExpenseMgr].[user_schema].[user]
set is_admin = 1 where user_key = 2

create database ExpenseMgrTest


USE ExpenseMgrTest;
GO

CREATE SCHEMA user_schema
GO

CREATE SCHEMA money_schema
GO

select * from [money_schema].[currency]
select * from [money_schema].[division_by]