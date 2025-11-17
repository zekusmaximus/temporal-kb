# kb/core/models.py

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, synonym
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all ORM models"""

    pass


def generate_id(prefix: str = "ent") -> str:
    """Generate prefixed UUID for easier debugging"""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: generate_id("ent"))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    entry_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String, unique=True)
    source: Mapped[Optional[str]] = mapped_column(String)
    source_metadata: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    word_count: Mapped[Optional[int]] = mapped_column(Integer)
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    vault_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("vaults.id"))

    # Relationships
    vault: Mapped[Optional["Vault"]] = relationship("Vault", back_populates="entries")
    versions: Mapped[list["EntryVersion"]] = relationship(
        "EntryVersion", back_populates="entry", cascade="all, delete-orphan"
    )
    tags: Mapped[list["Tag"]] = relationship("Tag", secondary="entry_tags", back_populates="entries")
    projects: Mapped[list["Project"]] = relationship(
        "Project", secondary="entry_projects", back_populates="entries"
    )
    outgoing_links: Mapped[list["EntryLink"]] = relationship(
        "EntryLink",
        foreign_keys="EntryLink.from_entry_id",
        back_populates="from_entry",
        cascade="all, delete-orphan",
    )
    incoming_links: Mapped[list["EntryLink"]] = relationship(
        "EntryLink",
        foreign_keys="EntryLink.to_entry_id",
        back_populates="to_entry",
        cascade="all, delete-orphan",
    )
    embedding: Mapped[Optional["Embedding"]] = relationship(
        "Embedding", back_populates="entry", uselist=False
    )

    def __repr__(self):
        return f"<Entry(id={self.id}, title='{self.title[:30]}...', type={self.entry_type})>"


class EntryVersion(Base):
    __tablename__ = "entry_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: generate_id("ver"))
    entry_id: Mapped[str] = mapped_column(String, ForeignKey("entries.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    change_type: Mapped[Optional[str]] = mapped_column(String)  # 'create', 'edit', 'merge', 'split'
    change_summary: Mapped[Optional[str]] = mapped_column(Text)
    diff_stats: Mapped[Optional[str]] = mapped_column(Text)  # JSON

    entry: Mapped["Entry"] = relationship("Entry", back_populates="versions")

    __table_args__ = (UniqueConstraint("entry_id", "version_number", name="uq_entry_version"),)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: generate_id("tag"))
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String)  # 'domain', 'project', 'theme', 'status'
    color: Mapped[Optional[str]] = mapped_column(String)
    parent_tag_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("tags.id"))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=func.now())

    entries: Mapped[list["Entry"]] = relationship(
        "Entry", secondary="entry_tags", back_populates="tags"
    )
    children: Mapped[list["Tag"]] = relationship("Tag", back_populates="parent", remote_side=[id])
    parent: Mapped[Optional["Tag"]] = relationship("Tag", back_populates="children", remote_side=[parent_tag_id])


class EntryTag(Base):
    __tablename__ = "entry_tags"

    entry_id: Mapped[str] = mapped_column(String, ForeignKey("entries.id"), primary_key=True)
    tag_id: Mapped[str] = mapped_column(String, ForeignKey("tags.id"), primary_key=True)
    added_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=func.now())
    confidence: Mapped[float] = mapped_column(Float, default=1.0)


class EntryLink(Base):
    __tablename__ = "entry_links"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: generate_id("lnk"))
    from_entry_id: Mapped[str] = mapped_column(String, ForeignKey("entries.id"), nullable=False)
    to_entry_id: Mapped[str] = mapped_column(String, ForeignKey("entries.id"), nullable=False)
    link_type: Mapped[str] = mapped_column(String, nullable=False)
    strength: Mapped[float] = mapped_column(Float, default=1.0)
    context: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=func.now())
    is_automatic: Mapped[bool] = mapped_column(Boolean, default=False)

    from_entry: Mapped["Entry"] = relationship(
        "Entry", foreign_keys=[from_entry_id], back_populates="outgoing_links"
    )
    to_entry: Mapped["Entry"] = relationship(
        "Entry", foreign_keys=[to_entry_id], back_populates="incoming_links"
    )

    __table_args__ = (
        UniqueConstraint("from_entry_id", "to_entry_id", "link_type", name="uq_entry_link"),
    )

    # Backward-compatible attribute names used in tests
    source_id = synonym("from_entry_id")
    target_id = synonym("to_entry_id")


class Person(Base):
    __tablename__ = "people"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: generate_id("per"))
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String)
    contact_info: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    notes: Mapped[Optional[str]] = mapped_column(Text)

    entries: Mapped[list["Entry"]] = relationship("Entry", secondary="entry_people")


class EntryPerson(Base):
    __tablename__ = "entry_people"

    entry_id: Mapped[str] = mapped_column(String, ForeignKey("entries.id"), primary_key=True)
    person_id: Mapped[str] = mapped_column(String, ForeignKey("people.id"), primary_key=True)
    mention_context: Mapped[Optional[str]] = mapped_column(Text)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: generate_id("prj"))
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    project_type: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[Optional[str]] = mapped_column(String)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    description: Mapped[Optional[str]] = mapped_column(Text)
    parent_project_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("projects.id"))

    entries: Mapped[list["Entry"]] = relationship(
        "Entry", secondary="entry_projects", back_populates="projects"
    )
    children: Mapped[list["Project"]] = relationship(
        "Project", back_populates="parent", remote_side=[id]
    )
    parent: Mapped[Optional["Project"]] = relationship(
        "Project", back_populates="children", remote_side=[parent_project_id]
    )


class EntryProject(Base):
    __tablename__ = "entry_projects"

    entry_id: Mapped[str] = mapped_column(String, ForeignKey("entries.id"), primary_key=True)
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id"), primary_key=True)
    role: Mapped[Optional[str]] = mapped_column(String)


class TemporalEvent(Base):
    __tablename__ = "temporal_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: generate_id("evt"))
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    event_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    entry_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("entries.id"))
    project_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("projects.id"))
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_rule: Mapped[Optional[str]] = mapped_column(String)


class QueryHistory(Base):
    __tablename__ = "query_history"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: generate_id("qry"))
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[Optional[str]] = mapped_column(String)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=func.now(), index=True)
    results_count: Mapped[Optional[int]] = mapped_column(Integer)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    result_entry_ids: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    context: Mapped[Optional[str]] = mapped_column(Text)  # JSON


class Vault(Base):
    __tablename__ = "vaults"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: generate_id("vlt"))
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    encryption_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=func.now())

    entries: Mapped[list["Entry"]] = relationship("Entry", back_populates="vault")


class Embedding(Base):
    __tablename__ = "embeddings"

    entry_id: Mapped[str] = mapped_column(String, ForeignKey("entries.id"), primary_key=True)
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    embedding_version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=func.now())
    last_updated: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    entry: Mapped["Entry"] = relationship("Entry", back_populates="embedding")
