/* Table: users
   Target: MS SQL Server 2016
*/
USE [MSS301_2026_PE_MEDIA]
GO

CREATE TABLE [dbo].[users] (
    [user_id]         INT              IDENTITY(1,1) NOT NULL, -- Auto increment
    [username]        NVARCHAR(30)     NOT NULL,               -- Unique
    [email]           NVARCHAR(100)    NOT NULL,
    [role]            NVARCHAR(15)     NOT NULL,
    [rate_per_post]   DECIMAL(18,2)    NOT NULL,
    [max_daily_posts] INT              NOT NULL,
    [level]           INT              NOT NULL,
    [status]          NVARCHAR(15)     NOT NULL,

    -- Primary Key
    CONSTRAINT [PK_Users] PRIMARY KEY CLUSTERED ([user_id] ASC),

    -- Unique username
    CONSTRAINT [UQ_Users_Username] UNIQUE NONCLUSTERED ([username] ASC),

    -- Role allowed values
    CONSTRAINT [CK_Users_Role]
        CHECK ([role] IN ('USER', 'CREATOR', 'ADMIN')),

    -- Rate must be greater than 0
    CONSTRAINT [CK_Users_Rate]
        CHECK ([rate_per_post] > 0),

    -- max_daily_posts between 1 and 10
    CONSTRAINT [CK_Users_MaxDaily]
        CHECK ([max_daily_posts] >= 1 AND [max_daily_posts] <= 10),

    -- level must be >= 1
    CONSTRAINT [CK_Users_Level]
        CHECK ([level] >= 1),

    -- Status allowed values
    CONSTRAINT [CK_Users_Status]
        CHECK ([status] IN ('ACTIVE', 'SUSPENDED', 'DEACTIVATED'))
);
GO
