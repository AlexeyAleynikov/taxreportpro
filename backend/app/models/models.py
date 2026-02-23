"""SQLAlchemy модели TaxReport Pro."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, DateTime, Enum, ForeignKey,
    Integer, JSON, Numeric, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ── Перечисления ──────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    client = "client"


class Jurisdiction(str, enum.Enum):
    RU = "RU"
    US = "US"
    BOTH = "BOTH"


class TaxYearStatus(str, enum.Enum):
    active = "active"
    archived = "archived"
    locked = "locked"


# ── Пользователи ──────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), default="")
    last_name: Mapped[str] = mapped_column(String(100), default="")
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.manager, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    clients: Mapped[list["Client"]] = relationship(back_populates="manager")


# ── Настройки системы ─────────────────────────────────────────────────────────

class SystemSettings(Base):
    """Глобальные настройки, управляемые администратором."""
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Ключи: "registration_open" (true/false), "default_locale" (ru/en), ...


# ── Клиенты (профили налогоплательщика) ──────────────────────────────────────

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(300), nullable=False)
    # ИНН / TIN — хранится в зашифрованном виде
    inn_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tin_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    country: Mapped[str] = mapped_column(String(2), nullable=False)  # RU | US
    region_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    manager: Mapped["User"] = relationship(back_populates="clients")
    tax_years: Mapped[list["TaxYear"]] = relationship(back_populates="client", cascade="all, delete-orphan")


# ── Налоговые годы ────────────────────────────────────────────────────────────

class TaxYear(Base):
    __tablename__ = "tax_years"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)
    jurisdiction: Mapped[Jurisdiction] = mapped_column(Enum(Jurisdiction), nullable=False)
    tax_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # single/mfj/...
    status: Mapped[TaxYearStatus] = mapped_column(Enum(TaxYearStatus), default=TaxYearStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    client: Mapped["Client"] = relationship(back_populates="tax_years")
    documents: Mapped[list["TaxDocument"]] = relationship(back_populates="tax_year", cascade="all, delete-orphan")
    calc_result: Mapped[Optional["TaxCalcResult"]] = relationship(back_populates="tax_year", uselist=False)
    deductions: Mapped[list["DeductionItem"]] = relationship(back_populates="tax_year", cascade="all, delete-orphan")
    credits: Mapped[list["CreditItem"]] = relationship(back_populates="tax_year", cascade="all, delete-orphan")


# ── Налоговые документы ───────────────────────────────────────────────────────

class TaxDocument(Base):
    __tablename__ = "tax_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tax_year_id: Mapped[int] = mapped_column(ForeignKey("tax_years.id"), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(30), nullable=False)  # 2NDFL | W2 | 1099NEC | ...
    source_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ocr_raw: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tax_year: Mapped["TaxYear"] = relationship(back_populates="documents")
    income_items: Mapped[list["IncomeItem"]] = relationship(back_populates="document", cascade="all, delete-orphan")


# ── Позиции доходов ───────────────────────────────────────────────────────────

class IncomeItem(Base):
    __tablename__ = "income_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("tax_documents.id"), nullable=False)
    income_type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    withheld_tax: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    employer_name: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    document: Mapped["TaxDocument"] = relationship(back_populates="income_items")


# ── Вычеты ────────────────────────────────────────────────────────────────────

class DeductionItem(Base):
    __tablename__ = "deduction_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tax_year_id: Mapped[int] = mapped_column(ForeignKey("tax_years.id"), nullable=False)
    ded_type: Mapped[str] = mapped_column(String(50), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(2), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    applied_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tax_year: Mapped["TaxYear"] = relationship(back_populates="deductions")


# ── Налоговые кредиты (США) ───────────────────────────────────────────────────

class CreditItem(Base):
    __tablename__ = "credit_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tax_year_id: Mapped[int] = mapped_column(ForeignKey("tax_years.id"), nullable=False)
    credit_type: Mapped[str] = mapped_column(String(50), nullable=False)
    calculated_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    phase_out_applied: Mapped[bool] = mapped_column(Boolean, default=False)

    tax_year: Mapped["TaxYear"] = relationship(back_populates="credits")


# ── Результаты расчёта ────────────────────────────────────────────────────────

class TaxCalcResult(Base):
    __tablename__ = "tax_calc_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tax_year_id: Mapped[int] = mapped_column(ForeignKey("tax_years.id"), unique=True, nullable=False)
    jurisdiction: Mapped[Jurisdiction] = mapped_column(Enum(Jurisdiction), nullable=False)
    gross_income_ru: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    gross_income_us: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    taxable_income_ru: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    taxable_income_us: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    tax_due_ru: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    tax_due_us_federal: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    tax_due_us_state: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    tax_withheld_ru: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    tax_withheld_us: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    refund_or_owe_ru: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    refund_or_owe_us: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    effective_rate_ru: Mapped[Optional[float]] = mapped_column(Numeric(6, 4), nullable=True)
    effective_rate_us: Mapped[Optional[float]] = mapped_column(Numeric(6, 4), nullable=True)
    calc_details: Mapped[dict] = mapped_column(JSON, default=dict)  # пошаговый разбор
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tax_year: Mapped["TaxYear"] = relationship(back_populates="calc_result")


# ── Справочник ставок ─────────────────────────────────────────────────────────

class RegionRateRef(Base):
    __tablename__ = "region_rate_refs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    region_code: Mapped[str] = mapped_column(String(20), nullable=False)
    region_name: Mapped[str] = mapped_column(String(200), nullable=False)
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)
    rate_type: Mapped[str] = mapped_column(String(50), nullable=False)
    rate_value: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False)
    limit_value: Mapped[Optional[float]] = mapped_column(Numeric(18, 2), nullable=True)


# ── Журнал аудита ─────────────────────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
