import datetime
import uuid

from sqlalchemy import String, Boolean, ForeignKey, Text, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, DATETIME2

from infrastructure.databases.database import Base


class LanguageDataModel(Base):
    __tablename__ = "languages"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_target_language: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_native_language: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class PhrasalVerbDataModel(Base):
    __tablename__ = "phrasal_verbs"
    __table_args__ = (
        UniqueConstraint("verb", "particle", "created_by_user_id", name="uq_verb_particle_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True)
    verb: Mapped[str] = mapped_column(String(100), nullable=False)
    particle: Mapped[str] = mapped_column(String(50), nullable=False)
    definition: Mapped[str] = mapped_column(String(500), nullable=False)
    example_sentence: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_catalog: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False)


class UserProfileDataModel(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=False, unique=True)
    native_language_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True),
        ForeignKey("languages.id"),
        nullable=False,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False)

    native_language = relationship("LanguageDataModel", lazy="joined")
    learning_languages = relationship(
        "UserLearningLanguageDataModel", back_populates="profile", lazy="joined")
    phrasal_verb_selections = relationship(
        "UserPhrasalVerbSelectionDataModel", back_populates="profile", lazy="selectin")


class UserLearningLanguageDataModel(Base):
    __tablename__ = "user_learning_languages"
    __table_args__ = (
        UniqueConstraint("user_id", "language_id", name="uq_user_learning_language"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True),
        ForeignKey("user_profiles.user_id"),
        nullable=False,
    )
    language_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True),
        ForeignKey("languages.id"),
        nullable=False,
    )

    profile = relationship("UserProfileDataModel", back_populates="learning_languages")
    language = relationship("LanguageDataModel", lazy="joined")


class UserPhrasalVerbSelectionDataModel(Base):
    __tablename__ = "user_phrasal_verb_selections"
    __table_args__ = (
        UniqueConstraint("user_id", "phrasal_verb_id", name="uq_user_phrasal_verb"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True),
        ForeignKey("user_profiles.user_id"),
        nullable=False,
    )
    phrasal_verb_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True),
        ForeignKey("phrasal_verbs.id"),
        nullable=False,
    )
    added_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False)

    profile = relationship("UserProfileDataModel", back_populates="phrasal_verb_selections")
    phrasal_verb = relationship("PhrasalVerbDataModel", lazy="joined")


class ExerciseResultDataModel(Base):
    __tablename__ = "exercise_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True), nullable=False, index=True)
    phrasal_verb_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True),
        ForeignKey("phrasal_verbs.id"),
        nullable=False,
    )
    exercise_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    scenario_native: Mapped[str] = mapped_column(Text, nullable=False)
    sentence_native: Mapped[str] = mapped_column(Text, nullable=False)
    sentence_target: Mapped[str] = mapped_column(Text, nullable=False)
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False)

    phrasal_verb = relationship("PhrasalVerbDataModel", lazy="joined")
