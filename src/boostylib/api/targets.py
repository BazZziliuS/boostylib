"""Targets (goals) API."""

from __future__ import annotations

from typing import Any

from boostylib.api.base import BaseAPI
from boostylib.enums import TargetType
from boostylib.models.target import Target


class TargetsAPI(BaseAPI):
    """Endpoints for blog goals/targets.

    Boosty supports two types of targets:
    - ``money`` — fundraising goal in currency
    - ``subscribers`` — subscriber count goal
    """

    async def get_target(self, target_id: int | str) -> Target:
        """Get a single target by ID.

        Args:
            target_id: Target identifier.

        Returns:
            Target model instance.
        """
        data = await self._get(f"/target/{target_id}")
        return Target.model_validate(data)

    async def create_target(
        self,
        username: str,
        *,
        description: str,
        target_sum: int,
        target_type: TargetType = TargetType.MONEY,
    ) -> Target:
        """Create a new target/goal.

        Args:
            username: Blog username (used as blog_url).
            description: Goal description text.
            target_sum: Target amount (currency or subscriber count).
            target_type: ``money`` or ``subscribers``.

        Returns:
            The created Target.
        """
        form_data = {
            "blog_url": username,
            "description": description,
            "target_sum": str(target_sum),
        }

        response = await self._transport.request(
            "POST",
            f"/target/{target_type.value}",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        data = response.json()
        return Target.model_validate(data)

    async def update_target(
        self,
        target_id: int | str,
        **kwargs: Any,
    ) -> Target:
        """Update a target.

        Args:
            target_id: Target identifier.
            **kwargs: Target attributes to update.

        Returns:
            Updated Target model instance.
        """
        form_data = {k: str(v) for k, v in kwargs.items()}
        response = await self._transport.request(
            "PUT",
            f"/target/{target_id}",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        data = response.json()
        return Target.model_validate(data)

    async def delete_target(self, target_id: int | str) -> None:
        """Delete a target.

        Args:
            target_id: Target identifier to delete.
        """
        await self._transport.request("DELETE", f"/target/{target_id}")
