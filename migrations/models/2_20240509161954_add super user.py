from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "is_superuser" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "users" ALTER COLUMN "taxpayer_id" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "is_superuser";
        ALTER TABLE "users" ALTER COLUMN "taxpayer_id" SET NOT NULL;"""
