from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.db.models.form_submission import Place, User, FormSubmission
from app.db.schemas.form_submission import (
    PlaceCreate, UserCreate, FormSubmissionCreate, FormSubmissionStatus
)


async def get_places(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Place]:
    result = await db.execute(select(Place).offset(skip).limit(limit))
    return result.scalars().all()


async def get_places_by_place_ids(db: AsyncSession, place_ids: List[str]) -> List[Place]:
    """
    Get places by their place_id strings (Google Places IDs).
    """
    result = await db.execute(select(Place).where(Place.place_id.in_(place_ids)))
    return result.scalars().all()


async def get_places_by_ids(db: AsyncSession, place_ids: List[int]) -> List[Place]:
    """
    Get places by their IDs.
    """
    result = await db.execute(select(Place).where(Place.id.in_(place_ids)))
    return result.scalars().all()


async def get_place_by_id(db: AsyncSession, place_id: int) -> Optional[Place]:
    result = await db.execute(select(Place).where(Place.id == place_id))
    return result.scalar_one_or_none()


async def create_place(db: AsyncSession, place: PlaceCreate) -> Place:
    db_place = Place(**place.model_dump())
    db.add(db_place)
    await db.commit()
    await db.refresh(db_place)
    return db_place


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_random_user(db: AsyncSession) -> Optional[User]:
    result = await db.execute(select(User).order_by(func.random()).limit(1))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def create_form_submission(
    db: AsyncSession, 
    submission: FormSubmissionCreate
) -> FormSubmission:
    db_submission = FormSubmission(**submission.model_dump())
    db.add(db_submission)
    await db.commit()
    await db.refresh(db_submission)
    return db_submission


async def update_form_submission_status(
    db: AsyncSession,
    submission_id: int,
    status: str,
    error_message: Optional[str] = None
) -> Optional[FormSubmission]:
    result = await db.execute(
        select(FormSubmission).where(FormSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    
    if submission:
        submission.submission_status = status
        if error_message:
            submission.error_message = error_message
        await db.commit()
        await db.refresh(submission)
    
    return submission


async def get_form_submissions(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100
) -> List[FormSubmission]:
    result = await db.execute(
        select(FormSubmission)
        .options(selectinload(FormSubmission.place), selectinload(FormSubmission.user))
        .offset(skip)
        .limit(limit)
        .order_by(FormSubmission.submitted_at.desc())
    )
    return result.scalars().all()


async def get_form_submissions_by_user_email(
    db: AsyncSession, 
    email: str,
    skip: int = 0, 
    limit: int = 100
) -> List[FormSubmission]:
    result = await db.execute(
        select(FormSubmission)
        .join(User, FormSubmission.user_id == User.id)
        .options(selectinload(FormSubmission.place), selectinload(FormSubmission.user))
        .where(User.email == email)
        .offset(skip)
        .limit(limit)
        .order_by(FormSubmission.submitted_at.desc())
    )
    return result.scalars().all()


async def get_submission_status(db: AsyncSession) -> FormSubmissionStatus:
    total_result = await db.execute(select(func.count(FormSubmission.id)))
    total = total_result.scalar()
    
    successful_result = await db.execute(
        select(func.count(FormSubmission.id))
        .where(FormSubmission.submission_status == "success")
    )
    successful = successful_result.scalar()
    
    failed_result = await db.execute(
        select(func.count(FormSubmission.id))
        .where(FormSubmission.submission_status == "failed")
    )
    failed = failed_result.scalar()
    
    pending_result = await db.execute(
        select(func.count(FormSubmission.id))
        .where(FormSubmission.submission_status == "pending")
    )
    pending = pending_result.scalar()
    
    recent_submissions = await get_form_submissions(db, limit=10)
    
    return FormSubmissionStatus(
        total_submissions=total,
        successful=successful,
        failed=failed,
        pending=pending,
        recent_submissions=recent_submissions
    )


async def check_existing_successful_submission(
    db: AsyncSession, 
    user_id: int, 
    place_id: int
) -> Optional[FormSubmission]:
    """
    Check if there's already a successful submission for this user and place combination.
    Returns the existing successful submission if found, None otherwise.
    """
    result = await db.execute(
        select(FormSubmission)
        .where(
            FormSubmission.user_id == user_id,
            FormSubmission.place_id == place_id,
            FormSubmission.submission_status == "success"
        )
        .order_by(FormSubmission.submitted_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def check_existing_skipped_submission(
    db: AsyncSession, 
    user_id: int,
    place_id: int
) -> Optional[FormSubmission]:
    """
    Check if there's already a skipped submission for this user and place combination.
    Returns the existing skipped submission if found, None otherwise.
    """
    result = await db.execute(
        select(FormSubmission)
        .where(
            FormSubmission.user_id == user_id,
            FormSubmission.place_id == place_id,
            FormSubmission.submission_status == "skipped"
        )
        .order_by(FormSubmission.submitted_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def check_existing_successful_or_skipped_submission(
    db: AsyncSession, 
    user_id: int, 
    place_id: int
) -> Optional[FormSubmission]:
    """
    Check if there's already a successful or skipped submission for this user and place combination.
    Returns the existing submission if found, None otherwise.
    """
    result = await db.execute(
        select(FormSubmission)
        .where(
            FormSubmission.user_id == user_id,
            FormSubmission.place_id == place_id,
            FormSubmission.submission_status.in_(["success", "skipped"])
        )
        .order_by(FormSubmission.submitted_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def check_existing_successful_or_skipped_submission_by_place_id(
    db: AsyncSession, 
    user_id: int, 
    place_id: str
) -> Optional[FormSubmission]:
    """
    Check if there's already a successful or skipped submission for this user and place_id combination.
    Returns the existing submission if found, None otherwise.
    """
    result = await db.execute(
        select(FormSubmission)
        .join(Place, FormSubmission.place_id == Place.id)
        .where(
            FormSubmission.user_id == user_id,
            Place.place_id == place_id,
            FormSubmission.submission_status.in_(["success", "skipped"])
        )
        .order_by(FormSubmission.submitted_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_user_submission_history(
    db: AsyncSession, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 50
) -> List[FormSubmission]:
    """
    Get submission history for a specific user.
    """
    result = await db.execute(
        select(FormSubmission)
        .options(selectinload(FormSubmission.place))
        .where(FormSubmission.user_id == user_id)
        .order_by(FormSubmission.submitted_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all() 