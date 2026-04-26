-- initial sql setup before alembic
-- create database ExpenseMgr
-- GO

-- USE ExpenseMgr
-- GO

-- CREATE SCHEMA user_schema
-- GO

-- CREATE SCHEMA money_schema
-- GO

-- drop all tables
-- drop table [money_schema].[expense_ver]
-- drop table [money_schema].[expense]
-- drop table [money_schema].[division_by]
-- drop table [money_schema].[currency]
-- drop table [user_schema].[user]
-- drop table [dbo].[alembic_version]

-- select from all tables
select * from [user_schema].[user]
select * from [money_schema].[currency]
select * from [money_schema].[division_by]
select * from [money_schema].[expense]
select * from [money_schema].[expense_ver]

-- initial admin update
-- update [ExpenseMgr].[user_schema].[user]
-- set is_admin = 1 where user_key = 2

-- insert division by types
-- insert into [ExpenseMgr].[money_schema].[division_by] (division_by_code, division_by_type_desc)values ('AMOUNT', 'Divide expense by amount'), ('PERCENTAGE', 'Divide expense by percentage')

-- delete from tables
-- delete from [user_schema].[user]
-- delete from [money_schema].[expense_ver]
-- delete from [money_schema].[expense]
-- delete from [money_schema].[currency]
-- delete from [money_schema].[division_by]

-- ideation for expenseout query

-- select
-- CONCAT(u2.first_name, ' ', u2.last_name) as primary_user_name,
-- CONCAT(u1.first_name, ' ', u1.last_name) as secondary_user_name,
-- ev.expense_share,
-- c.currency_code,
-- e.total_amount,
-- d.division_by_code,
-- e.expense_desc
-- from [money_schema].[expense] e
-- inner join [money_schema].[expense_ver] ev
-- on e.expense_key = ev.expense_key
-- inner join [user_schema].[user] u1
-- on ev.secondary_user_key = u1.user_key
-- inner join [user_schema].[user] u2
-- on e.primary_user_key = u2.user_key
-- inner join [money_schema].[currency] c
-- on e.currency_key = c.currency_key
-- inner join [money_schema].[division_by] d
-- on e.division_by_key = d.division_by_key
-- where e.expense_key=8

-- ideation for getting all expenses for a user

-- select
-- expense_key
-- from [money_schema].[expense_ver]
-- where secondary_user_key = 4

-- SELECT 
-- money_schema.expense.expense_key AS expense_key, 
-- concat(user_1.first_name, ' ', user_1.last_name) AS primary_user_name, 
-- concat(user_2.first_name, ' ', user_2.last_name) AS secondary_user_name, money_schema.expense_ver.expense_share AS expense_share, 
-- money_schema.currency.currency_code AS currency_code, 
-- money_schema.expense.total_amount AS total_amount, 
-- money_schema.division_by.division_by_code AS division_by_code, 
-- money_schema.expense.expense_desc AS expense_desc 
-- FROM 
-- money_schema.expense 
-- JOIN money_schema.expense_ver 
-- ON money_schema.expense.expense_key = money_schema.expense_ver.expense_key 
-- AND money_schema.expense.expense_key IN (
--     select
-- expense_key
-- from [money_schema].[expense_ver]
-- where secondary_user_key = 4
-- )
-- JOIN user_schema.[user] AS user_1 
-- ON money_schema.expense.primary_user_key = user_1.user_key 
-- JOIN user_schema.[user] AS user_2 
-- ON money_schema.expense_ver.secondary_user_key = user_2.user_key 
-- JOIN money_schema.currency 
-- ON money_schema.expense.currency_key = money_schema.currency.currency_key 
-- JOIN money_schema.division_by 
-- ON money_schema.expense.division_by_key = money_schema.division_by.division_by_key