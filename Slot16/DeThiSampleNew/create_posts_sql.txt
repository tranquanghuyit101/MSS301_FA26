USE [MSS301_2026_PE_MEDIA]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[posts](
    [post_id]          [int]           IDENTITY(1,1) NOT NULL,
    [advertiser_name]  [nvarchar](100) NOT NULL,
    [advertiser_email] [nvarchar](100) NOT NULL,
    [advertiser_phone] [nvarchar](20)  NOT NULL,
    [start_date]       [date]          NOT NULL,
    [end_date]         [date]          NOT NULL,
    [number_of_posts]  [int]           NOT NULL,
    [total_cost]       [decimal](18,2) NOT NULL,
    [status]           [nvarchar](15)  NOT NULL,
    [user_id]          [int]           NOT NULL,

 CONSTRAINT [PK_Posts] PRIMARY KEY CLUSTERED
(
    [post_id] ASC
) ON [PRIMARY]
) ON [PRIMARY]
GO

-- end_date must be after start_date
ALTER TABLE [dbo].[posts]
    WITH CHECK ADD CONSTRAINT [CK_Posts_Dates]
    CHECK ([end_date] > [start_date]);
GO
ALTER TABLE [dbo].[posts] CHECK CONSTRAINT [CK_Posts_Dates];
GO

-- number_of_posts must be >= 1
ALTER TABLE [dbo].[posts]
    WITH CHECK ADD CONSTRAINT [CK_Posts_Number]
    CHECK ([number_of_posts] >= 1);
GO
ALTER TABLE [dbo].[posts] CHECK CONSTRAINT [CK_Posts_Number];
GO

-- total_cost must be >= 0
ALTER TABLE [dbo].[posts]
    WITH CHECK ADD CONSTRAINT [CK_Posts_Cost]
    CHECK ([total_cost] >= 0);
GO
ALTER TABLE [dbo].[posts] CHECK CONSTRAINT [CK_Posts_Cost];
GO

-- Status allowed values
ALTER TABLE [dbo].[posts]
    WITH CHECK ADD CONSTRAINT [CK_Posts_Status]
    CHECK ([status] IN ('DRAFT', 'SCHEDULED', 'PUBLISHED', 'CANCELLED'));
GO
ALTER TABLE [dbo].[posts] CHECK CONSTRAINT [CK_Posts_Status];
GO

-- Foreign key to users
ALTER TABLE [dbo].[posts]
    WITH CHECK ADD CONSTRAINT [FK_Posts_User]
    FOREIGN KEY ([user_id]) REFERENCES [dbo].[users]([user_id]);
GO
ALTER TABLE [dbo].[posts] CHECK CONSTRAINT [FK_Posts_User];
GO
