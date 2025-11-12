# kb/api/routes/projects.py


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_session
from ...core.models import EntryProject, Project
from ...core.schemas import ProjectCreate
from ..dependencies import get_current_user

router = APIRouter()


@router.get("/")
async def list_projects(
    db: Session = Depends(get_session), current_user: dict = Depends(get_current_user)
):
    """List all projects with entry counts"""

    from sqlalchemy import func

    projects = (
        db.query(
            Project.id,
            Project.name,
            Project.project_type,
            Project.status,
            Project.description,
            func.count(EntryProject.entry_id).label("entry_count"),
        )
        .outerjoin(EntryProject)
        .group_by(Project.id)
        .order_by(func.count(EntryProject.entry_id).desc())
        .all()
    )

    return [
        {
            "id": proj.id,
            "name": proj.name,
            "type": proj.project_type,
            "status": proj.status,
            "description": proj.description,
            "entry_count": proj.entry_count,
        }
        for proj in projects
    ]


@router.post("/")
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Create a new project"""

    project = Project(
        name=project_data.name,
        project_type=project_data.project_type,
        status="active",
        description=project_data.description,
        parent_project_id=project_data.parent_project_id,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "id": project.id,
        "name": project.name,
        "type": project.project_type,
        "status": project.status,
    }
