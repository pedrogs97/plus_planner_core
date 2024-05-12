from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "profile_id" BIGINT;
        ALTER TABLE "users" ADD CONSTRAINT "fk_users_profiles_e431d96a" FOREIGN KEY ("profile_id") REFERENCES "profiles" ("id") ON DELETE SET NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP CONSTRAINT "fk_users_profiles_e431d96a";
        ALTER TABLE "users" DROP COLUMN "profile_id";"""
