"""Clinic office service"""

from typing import List

from plus_db_agent.models import (
    AnamnesisModel,
    BaseModel,
    DeskModel,
    PatientModel,
    PlanModel,
    PlanTreatmentModel,
    QuestionModel,
    SpecialtyModel,
    TreatmentModel,
    TreatmentPatientModel,
    UrgencyModel,
    UserModel,
)
from plus_db_agent.service import GenericService

from src.clinic_office.controller import (
    AnamnesisController,
    DeskController,
    PatientController,
    PlanController,
    QuestionController,
    SpecialtyController,
    TreatmentController,
    UrgencyController,
)
from src.clinic_office.schemas import (
    AnamnesisSerializerSchema,
    DeskSerializerSchema,
    PatientSerializerSchema,
    PlanSerializerSchema,
    QuestionSerializerSchema,
    SpecialtySerializerSchema,
    TreatmentSerializerSchema,
    UrgencySerializerSchema,
)


class PatientService(GenericService):
    """Patient service class"""

    def __init__(self) -> None:
        self.controller = PatientController()
        self.serializer = PatientSerializerSchema
        self.model = PatientModel
        self.module_name = "patient"

    async def list(self, **filters) -> List[dict]:
        super_list: List[PatientModel] = await super().list(**filters)
        return [{"id": patient.id, "name": patient.name} for patient in super_list]

    async def update(
        self, record: dict, pk: int, authenticated_user: UserModel
    ) -> BaseModel:
        treatments = record.pop("treatments")
        patient_dict = await super().update(record, pk, authenticated_user)
        if treatments:
            patient: PatientModel = await self.controller.get_obj_or_none(
                pk=patient_dict["id"]
            )
            if patient:
                await patient.fetch_related("treatments")
                treatments_db = await TreatmentModel.filter(
                    id__in=[treatment["id"] for treatment in treatments]
                ).all()
                await TreatmentPatientModel.filter(patient=patient).delete()
                treatments_patient_model = [
                    TreatmentPatientModel(
                        patient=patient,
                        treatment_id=treatment["id"],
                        start_date=treatment["start_date"],
                        end_date=treatment["end_date"],
                        observation=treatment["observation"],
                    )
                    for treatment in treatments_db
                ]
                await TreatmentPatientModel.bulk_create(treatments_patient_model)
                treatment_patients_db = await TreatmentPatientModel.filter(
                    patient=patient
                ).all()
                patient_dict["treatments"] = [
                    {
                        "id": treatment_patient.treatment.id,
                        "name": treatment_patient.treatment.name,
                        "startDate": treatment_patient.treatment.start_date,
                        "endDate": treatment_patient.treatment.end_date,
                        "observation": treatment_patient.treatment.observation,
                    }
                    for treatment_patient in treatment_patients_db
                ]
        return patient_dict


class UrgencyService(GenericService):
    """Urgency service class"""

    def __init__(self) -> None:
        self.model = UrgencyModel
        self.controller = UrgencyController()
        self.serializer = UrgencySerializerSchema
        self.module_name = "urgency"

    async def list(self, **filters) -> List[dict]:
        list_objs: List[UrgencyModel] = await self.controller.list(**filters)
        return [
            {"id": urgency.id, "name": urgency.name, "description": urgency.description}
            for urgency in list_objs
        ]

    async def add(self, record: dict, authenticated_user: UserModel) -> dict:
        patient = await PatientModel.get(id=record["patient"])
        record.update({"patient": patient})
        return await super().add(record, authenticated_user)

    async def update(
        self, record: dict, pk: int, authenticated_user: UserModel
    ) -> dict:
        patient = await PatientModel.get(id=record["patient"])
        record.update({"patient": patient})
        return await super().update(record, pk, authenticated_user)


class SpecialtyService(GenericService):
    """Specialty service"""

    def __init__(self) -> None:
        self.model = SpecialtyModel
        self.controller = SpecialtyController()
        self.serializer = SpecialtySerializerSchema
        self.module_name = "specialty"

    async def list(self, **filters) -> List[dict]:
        list_objs: List[SpecialtyModel] = await self.controller.list(**filters)
        return [{"id": specialty.id, "name": specialty.name} for specialty in list_objs]


class TreatmentService(GenericService):
    """Treatment service class"""

    def __init__(self) -> None:
        self.model = TreatmentModel
        self.controller = TreatmentController()
        self.serializer = TreatmentSerializerSchema
        self.module_name = "treatment"

    async def list(self, **filters) -> List[dict]:
        list_objs: List[TreatmentModel] = await self.controller.list(**filters)
        return [
            {"id": treatment.id, "name": treatment.name, "number": treatment.number}
            for treatment in list_objs
        ]


class PlanService(GenericService):
    """Plan service class"""

    def __init__(self) -> None:
        self.model = PlanModel
        self.controller = PlanController()
        self.serializer = PlanSerializerSchema
        self.module_name = "plan"

    async def list(self, **filters) -> List[dict]:
        list_objs: List[PlanModel] = await self.controller.list(**filters)
        return [{"id": plan.id, "name": plan.name} for plan in list_objs]

    async def add(self, record: dict, authenticated_user: UserModel) -> dict:
        specialties = record.pop("specialties")
        treatment_plans = record.pop("treatment_plans")
        plan_dict = await super().add(record, authenticated_user)
        if specialties:
            plan: PlanModel = await self.controller.get_obj_or_none(pk=plan_dict["id"])
            if plan:
                await plan.fetch_related("specialties")
                specialties_db = await SpecialtyModel.filter(id__in=specialties).all()
                await plan.specialties.add(specialties_db)
                plan_dict["specialties"] = [
                    {"id": specialty.id, "name": specialty.name}
                    for specialty in specialties_db
                ]

        if treatment_plans:
            plan: PlanModel = await self.controller.get_obj_or_none(pk=plan_dict["id"])
            if plan:
                await plan.fetch_related("treatment_plans")
                treatments_db = await TreatmentModel.filter(
                    id__in=treatment_plans
                ).all()
                treatments_plan_model = [
                    PlanTreatmentModel(plan=plan, treatment=treatment)
                    for treatment in treatments_db
                ]
                await PlanTreatmentModel.bulk_create(treatments_plan_model)
                treatment_plans_db = await PlanTreatmentModel.filter(plan=plan).all()
                plan_dict["treatment_plans"] = [
                    {
                        "id": treatment_plan.treatment.id,
                        "name": treatment_plan.treatment.name,
                        "number": treatment_plan.treatment.number,
                        "cost": treatment_plan.treatment.cost,
                        "value": treatment_plan.treatment.value,
                    }
                    for treatment_plan in treatment_plans_db
                ]
        return plan_dict

    async def update(
        self, record: dict, pk: int, authenticated_user: UserModel
    ) -> dict:
        specialties = record.pop("specialties")
        treatment_plans = record.pop("treatment_plans")
        plan_dict = await super().update(record, pk, authenticated_user)
        if specialties:
            plan: PlanModel = await self.controller.get_obj_or_none(pk=plan_dict["id"])
            if plan:
                await plan.fetch_related("specialties")
                specialties_db = await SpecialtyModel.filter(id__in=specialties).all()
                await plan.specialties.clear()
                await plan.specialties.add(specialties_db)
                plan_dict["specialties"] = [
                    {"id": specialty.id, "name": specialty.name}
                    for specialty in specialties_db
                ]
        if treatment_plans:
            plan: PlanModel = await self.controller.get_obj_or_none(pk=plan_dict["id"])
            if plan:
                await plan.fetch_related("treatment_plans")
                treatments_db = await TreatmentModel.filter(
                    id__in=treatment_plans
                ).all()
                await PlanTreatmentModel.filter(plan=plan).delete()
                treatments_plan_model = [
                    PlanTreatmentModel(plan=plan, treatment=treatment)
                    for treatment in treatments_db
                ]
                await PlanTreatmentModel.bulk_create(treatments_plan_model)
                treatment_plans_db = await PlanTreatmentModel.filter(plan=plan).all()
                plan_dict["treatment_plans"] = [
                    {
                        "id": treatment_plan.treatment.id,
                        "name": treatment_plan.treatment.name,
                        "number": treatment_plan.treatment.number,
                        "cost": treatment_plan.treatment.cost,
                        "value": treatment_plan.treatment.value,
                    }
                    for treatment_plan in treatment_plans_db
                ]

        return plan_dict

    async def delete(self, pk: int, authenticated_user: UserModel) -> None:
        plan: PlanModel = await self.controller.get_obj_or_none(pk=pk)
        if plan:
            await plan.fetch_related("specialties")
            await plan.specialties.clear()
            await PlanTreatmentModel.filter(plan=plan).delete()
        return await super().delete(pk, authenticated_user)


class DeskService(GenericService):
    """Desk service class"""

    def __init__(self) -> None:
        self.model = DeskModel
        self.controller = DeskController()
        self.serializer = DeskSerializerSchema
        self.module_name = "desk"

    async def list(self, **filters) -> List[dict]:
        list_objs: List[DeskModel] = await self.controller.list(**filters)
        return [{"id": desk.id, "number": desk.number} for desk in list_objs]


class AnamnesisService(GenericService):
    """Anamnesis service class"""

    def __init__(self) -> None:
        self.model = AnamnesisModel
        self.controller = AnamnesisController()
        self.serializer = AnamnesisSerializerSchema
        self.module_name = "anamnesis"

    async def list(self, **filters) -> List[dict]:
        list_objs: List[AnamnesisModel] = await self.controller.list(**filters)
        return [
            {"id": anamnesis.id, "name": anamnesis.name, "number": anamnesis.number}
            for anamnesis in list_objs
        ]

    async def add(self, record: dict, authenticated_user: UserModel) -> dict:
        questions = record.pop("questions")
        anamnesis_dict = await super().add(record, authenticated_user)
        if questions:
            anamnesis: AnamnesisModel = await self.controller.get_obj_or_none(
                pk=anamnesis_dict["id"]
            )
            if anamnesis:
                await anamnesis.fetch_related("questions")
                questions_db = await QuestionModel.filter(id__in=questions).all()
                await anamnesis.questions.add(questions_db)
                anamnesis_dict["questions"] = [
                    {"id": question.id, "question": question.question}
                    for question in questions_db
                ]
        return anamnesis_dict

    async def update(
        self, record: dict, pk: int, authenticated_user: UserModel
    ) -> dict:
        questions = record.pop("questions")
        anamnesis_dict = await super().update(record, pk, authenticated_user)
        if questions:
            anamnesis: AnamnesisModel = await self.controller.get_obj_or_none(
                pk=anamnesis_dict["id"]
            )
            if anamnesis:
                await anamnesis.fetch_related("questions")
                questions_db = await QuestionModel.filter(id__in=questions).all()
                await anamnesis.questions.clear()
                await anamnesis.questions.add(questions_db)
                anamnesis_dict["questions"] = [
                    {"id": question.id, "question": question.question}
                    for question in questions_db
                ]
        return anamnesis_dict


class QuestionService(GenericService):
    """Question service class"""

    def __init__(self) -> None:
        self.model = QuestionModel
        self.controller = QuestionController()
        self.serializer = QuestionSerializerSchema
        self.module_name = "question"
