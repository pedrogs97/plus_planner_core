from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "tokens" ALTER COLUMN "token" TYPE VARCHAR(500) USING "token"::VARCHAR(500);
        ALTER TABLE "tokens" ALTER COLUMN "refresh_token" TYPE VARCHAR(500) USING "refresh_token"::VARCHAR(500);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "tokens" ALTER COLUMN "token" TYPE VARCHAR(255) USING "token"::VARCHAR(255);
        ALTER TABLE "tokens" ALTER COLUMN "refresh_token" TYPE VARCHAR(255) USING "refresh_token"::VARCHAR(255);"""
