"""REST router of M-03 Placements (first vertical slice)."""

from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from horizon.config import get_settings
from horizon.infrastructure.database import get_db_session
from horizon.mocks.dh05_services import MockEmployerDirectoryService
from horizon.modules.access.policy import AccessDenied, AccessPolicy, Actor
from horizon.modules.integrations.adapters import EmployerDirectoryAdapter, IdentityAdapter
from horizon.modules.notifications.outbox import on_placement_activated
from horizon.modules.placements.domain import ActivationBlocked, IllegalTransition, StaleState
from horizon.modules.placements.service import ActivatePlacement, PlacementNotFound, ReadinessView
from horizon.modules.readiness.gate import ReadinessGate
from horizon.modules.rules.evaluators import RuleConfiguration
from horizon.shared.events import EventDispatcher

router = APIRouter(prefix="/placements", tags=["placements (M-03)"])


# ---- wiring (kept explicit and small; tests override these dependencies) ----
def get_dispatcher() -> EventDispatcher:
    dispatcher = EventDispatcher()
    dispatcher.subscribe("PlacementActivated", on_placement_activated)
    return dispatcher


def get_employer_directory() -> EmployerDirectoryAdapter:
    settings = get_settings()
    return EmployerDirectoryAdapter(
        MockEmployerDirectoryService(settings.mocks_root, settings.mock_employer_failure)
    )


def get_access_policy() -> AccessPolicy:
    return AccessPolicy(get_settings().data_root)


def get_today() -> date:
    return date.today()


def get_current_actor(
    x_mock_user_id: str | None = Header(default=None, alias="X-Mock-User-Id"),
    access: AccessPolicy = Depends(get_access_policy),
) -> Actor:
    if not get_settings().mock_identity_enabled:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Identity provider is not configured; the mock identity is disabled.",
        )
    if not x_mock_user_id:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "X-Mock-User-Id header is required in development mode."
        )
    identity = IdentityAdapter(get_settings().data_root).resolve(x_mock_user_id)
    if identity is None or not identity.active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unknown or inactive mock user.")
    return access.actor_for(identity)


def _gate(session: Session, directory) -> ReadinessGate:
    rules = RuleConfiguration(get_settings().rules_root / "readiness.json")
    return ReadinessGate(session, rules, directory)


def _to_http(error: Exception):
    if isinstance(error, PlacementNotFound) or (
        isinstance(error, AccessDenied) and not error.reveal
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Placement not found.")
    if isinstance(error, AccessDenied):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "You are not allowed to perform this action."
        )
    raise error


# ---- endpoints ------------------------------------------------------------------
@router.get("/{placement_id}/readiness")
def readiness(
    placement_id: str,
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_db_session),
    directory=Depends(get_employer_directory),
    access: AccessPolicy = Depends(get_access_policy),
    today: date = Depends(get_today),
) -> dict:
    view = ReadinessView(
        session, _gate(session, directory), access, lambda: today, lambda: datetime.now(UTC)
    )
    try:
        return view.execute(placement_id, actor)
    except (PlacementNotFound, AccessDenied) as error:
        _to_http(error)


@router.post("/{placement_id}/activation")
def activate(
    placement_id: str,
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_db_session),
    directory=Depends(get_employer_directory),
    access: AccessPolicy = Depends(get_access_policy),
    dispatcher: EventDispatcher = Depends(get_dispatcher),
    today: date = Depends(get_today),
):
    use_case = ActivatePlacement(
        session,
        _gate(session, directory),
        access,
        lambda: today,
        lambda: datetime.now(UTC),
        dispatcher=dispatcher,
    )
    try:
        return use_case.execute(placement_id, actor)
    except ActivationBlocked as blocked:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "code": "ACTIVATION_BLOCKED",
                "detail": "Activation refused: required conditions are not satisfied.",
                "blocking": [b.__dict__ for b in blocked.blocking],
                "correlation_id": blocked.correlation_id,
            },
        )
    except StaleState:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "code": "STATE_CHANGED",
                "detail": "The placement changed while the command was running. Read it again.",
            },
        )
    except IllegalTransition as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"code": "ILLEGAL_TRANSITION", "detail": str(error)},
        )
    except (PlacementNotFound, AccessDenied) as error:
        _to_http(error)
