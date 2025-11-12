# kb/core/models.py

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_id(prefix: str = "ent") -> str:
    """Generate prefixed UUID for easier debugging"""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

class Entry(Base):
    __tablename__ = "entries"
    
    id = Column(String, primary_key=True, default=lambda: generate_id("ent"))
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    entry_type = Column(String, nullable=False, index=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String, nullable=False)
    file_path = Column(String, unique=True)
    source = Column(String)
    source_metadata = Column(Text)  # JSON
    word_count = Column(Integer)
    is_encrypted = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    vault_id = Column(String, ForeignKey("vaults.id"))
    
    # Relationships
    vault = relationship("Vault", back_populates="entries")
    versions = relationship("EntryVersion", back_populates="entry", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="entry_tags", back_populates="entries")
    projects = relationship("Project", secondary="entry_projects", back_populates="entries")
    outgoing_links = relationship(
        "EntryLink",
        foreign_keys="EntryLink.from_entry_id",
        back_populates="from_entry",
        cascade="all, delete-orphan"
    )
    incoming_links = relationship(
        "EntryLink",
        foreign_keys="EntryLink.to_entry_id",
        back_populates="to_entry",
        cascade="all, delete-orphan"
    )
    embedding = relationship("Embedding", back_populates="entry", uselist=False)
    
    def __repr__(self):
        return f"<Entry(id={self.id}, title='{self.title[:30]}...', type={self.entry_type})>"


class EntryVersion(Base):
    __tablename__ = "entry_versions"
    
    id = Column(String, primary_key=True, default=lambda: generate_id("ver"))
    entry_id = Column(String, ForeignKey("entries.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String, nullable=False)
    changed_at = Column(DateTime, nullable=False, default=func.now())
    change_type = Column(String)  # 'create', 'edit', 'merge', 'split'
    change_summary = Column(Text)
    diff_stats = Column(Text)  # JSON
    
    entry = relationship("Entry", back_populates="versions")
    
    __table_args__ = (
        UniqueConstraint('entry_id', 'version_number', name='uq_entry_version'),
    )


class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(String, primary_key=True, default=lambda: generate_id("tag"))
    name = Column(String, unique=True, nullable=False)
    category = Column(String)  # 'domain', 'project', 'theme', 'status'
    color = Column(String)
    parent_tag_id = Column(String, ForeignKey("tags.id"))
    
    entries = relationship("Entry", secondary="entry_tags", back_populates="tags")
    children = relationship("Tag", backref="parent", remote_side=[id])


class EntryTag(Base):
    __tablename__ = "entry_tags"
    
    entry_id = Column(String, ForeignKey("entries.id"), primary_key=True)
    tag_id = Column(String, ForeignKey("tags.id"), primary_key=True)
    added_at = Column(DateTime, default=func.now())
    confidence = Column(Float, default=1.0)


class EntryLink(Base):
    __tablename__ = "entry_links"
    
    id = Column(String, primary_key=True, default=lambda: generate_id("lnk"))
    from_entry_id = Column(String, ForeignKey("entries.id"), nullable=False)
    to_entry_id = Column(String, ForeignKey("entries.id"), nullable=False)
    link_type = Column(String, nullable=False)
    strength = Column(Float, default=1.0)
    context = Column(Text)
    created_at = Column(DateTime, default=func.now())
    is_automatic = Column(Boolean, default=False)
    
    from_entry = relationship("Entry", foreign_keys=[from_entry_id], back_populates="outgoing_links")
    to_entry = relationship("Entry", foreign_keys=[to_entry_id], back_populates="incoming_links")
    
    __table_args__ = (
        UniqueConstraint('from_entry_id', 'to_entry_id', 'link_type', name='uq_entry_link'),
    )


class Person(Base):
    __tablename__ = "people"
    
    id = Column(String, primary_key=True, default=lambda: generate_id("per"))
    name = Column(String, unique=True, nullable=False)
    role = Column(String)
    contact_info = Column(Text)  # JSON
    notes = Column(Text)
    
    entries = relationship("Entry", secondary="entry_people")


class EntryPerson(Base):
    __tablename__ = "entry_people"
    
    entry_id = Column(String, ForeignKey("entries.id"), primary_key=True)
    person_id = Column(String, ForeignKey("people.id"), primary_key=True)
    mention_context = Column(Text)


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: generate_id("prj"))
    name = Column(String, unique=True, nullable=False)
    project_type = Column(String)
    status = Column(String)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    description = Column(Text)
    parent_project_id = Column(String, ForeignKey("projects.id"))
    
    entries = relationship("Entry", secondary="entry_projects", back_populates="projects")
    children = relationship("Project", backref="parent", remote_side=[id])


class EntryProject(Base):
    __tablename__ = "entry_projects"
    
    entry_id = Column(String, ForeignKey("entries.id"), primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), primary_key=True)
    role = Column(String)


class TemporalEvent(Base):
    __tablename__ = "temporal_events"
    
    id = Column(String, primary_key=True, default=lambda: generate_id("evt"))
    event_type = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    entry_id = Column(String, ForeignKey("entries.id"))
    project_id = Column(String, ForeignKey("projects.id"))
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String)


class QueryHistory(Base):
    __tablename__ = "query_history"
    
    id = Column(String, primary_key=True, default=lambda: generate_id("qry"))
    query_text = Column(Text, nullable=False)
    query_type = Column(String)
    executed_at = Column(DateTime, default=func.now(), index=True)
    results_count = Column(Integer)
    execution_time_ms = Column(Integer)
    result_entry_ids = Column(Text)  # JSON
    context = Column(Text)  # JSON


class Vault(Base):
    __tablename__ = "vaults"
    
    id = Column(String, primary_key=True, default=lambda: generate_id("vlt"))
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    encryption_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    entries = relationship("Entry", back_populates="vault")


class Embedding(Base):
    __tablename__ = "embeddings"
    
    entry_id = Column(String, ForeignKey("entries.id"), primary_key=True)
    model_name = Column(String, nullable=False)
    embedding_version = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    
    entry = relationship("Entry", back_populates="embedding")