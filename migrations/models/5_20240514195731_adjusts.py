from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "clinics" RENAME COLUMN "head_quarters_id" TO "head_quarter_id";
        ALTER TABLE "clinics" ADD "logo_path" VARCHAR(255);
        ALTER TABLE "clinics" ADD "subdomain" VARCHAR(255) NOT NULL UNIQUE;
        ALTER TABLE "clinics" ALTER COLUMN "legal_entity" SET DEFAULT False;
        ALTER TABLE "clinics" ALTER COLUMN "legal_entity" TYPE BOOL USING "legal_entity"::BOOL;
        ALTER TABLE "users" ADD "clinic_id" BIGINT;
        CREATE UNIQUE INDEX "uid_clinics_subdoma_78c756" ON "clinics" ("subdomain");
        ALTER TABLE "clinics" ADD CONSTRAINT "fk_clinics_clinics_00560b85" FOREIGN KEY ("head_quarter_id") REFERENCES "clinics" ("id") ON DELETE NO ACTION;
        ALTER TABLE "users" ADD CONSTRAINT "fk_users_clinics_86dea6c9" FOREIGN KEY ("clinic_id") REFERENCES "clinics" ("id") ON DELETE SET NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "clinics" DROP CONSTRAINT "fk_clinics_clinics_00560b85";
        DROP INDEX "idx_clinics_subdoma_78c756";
        ALTER TABLE "users" DROP CONSTRAINT "fk_users_clinics_86dea6c9";
        ALTER TABLE "users" DROP COLUMN "clinic_id";
        ALTER TABLE "clinics" RENAME COLUMN "head_quarter_id" TO "head_quarters_id";
        ALTER TABLE "clinics" DROP COLUMN "logo_path";
        ALTER TABLE "clinics" DROP COLUMN "subdomain";
        ALTER TABLE "clinics" ALTER COLUMN "legal_entity" TYPE VARCHAR(255) USING "legal_entity"::VARCHAR(255);
        ALTER TABLE "clinics" ALTER COLUMN "legal_entity" DROP DEFAULT;"""
