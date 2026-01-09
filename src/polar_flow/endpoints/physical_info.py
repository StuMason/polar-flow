"""Physical information endpoint for Polar AccessLink API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from polar_flow.models.physical_info import PhysicalInformation, PhysicalInfoTransaction

if TYPE_CHECKING:
    from polar_flow.client import PolarFlow


class PhysicalInfoEndpoint:
    """Physical information endpoint with transaction-based access.

    Physical information uses a transaction pattern:
    1. Create transaction
    2. List/get physical information within transaction
    3. Commit transaction to mark data as retrieved
    """

    def __init__(self, client: PolarFlow) -> None:
        """Initialize physical info endpoint.

        Args:
            client: PolarFlow client instance
        """
        self.client = client

    async def create_transaction(self, user_id: int | str) -> PhysicalInfoTransaction | None:
        """Create transaction to access new physical information.

        Args:
            user_id: Polar user ID

        Returns:
            Transaction metadata if new data available, None if no new data

        Raises:
            NotFoundError: If user not found
        """
        path = f"/v3/users/{user_id}/physical-information-transactions"
        response = await self.client._request("POST", path)

        # 204 No Content means no new data available
        if not response:
            return None

        return PhysicalInfoTransaction.model_validate(response)

    async def list_physical_info(self, user_id: int | str, transaction_id: int) -> list[str]:
        """List physical information URLs in transaction.

        Args:
            user_id: Polar user ID
            transaction_id: Transaction ID from create_transaction

        Returns:
            List of physical information resource URLs
        """
        path = f"/v3/users/{user_id}/physical-information-transactions/{transaction_id}"
        response = await self.client._request("GET", path)

        physical_infos: list[str] = response.get("physical-informations", [])
        return physical_infos

    async def get_physical_info(
        self, user_id: int | str, transaction_id: int, physical_info_id: int
    ) -> PhysicalInformation:
        """Get specific physical information entity.

        Args:
            user_id: Polar user ID
            transaction_id: Transaction ID
            physical_info_id: Physical information entity ID

        Returns:
            Physical information with body metrics

        Raises:
            NotFoundError: If physical info not found
        """
        path = f"/v3/users/{user_id}/physical-information-transactions/{transaction_id}/physical-informations/{physical_info_id}"
        response = await self.client._request("GET", path)
        return PhysicalInformation.model_validate(response)

    async def commit_transaction(self, user_id: int | str, transaction_id: int) -> None:
        """Commit transaction and mark data as retrieved.

        This should be called after retrieving all physical information
        to indicate the data has been successfully processed.

        Args:
            user_id: Polar user ID
            transaction_id: Transaction ID to commit
        """
        path = f"/v3/users/{user_id}/physical-information-transactions/{transaction_id}"
        await self.client._request("PUT", path)

    async def get_all(self, user_id: int | str) -> list[PhysicalInformation]:
        """Convenience method to get all new physical information.

        This creates a transaction, retrieves all physical info, and commits.

        Args:
            user_id: Polar user ID

        Returns:
            List of physical information records (empty if no new data)
        """
        # Create transaction
        transaction = await self.create_transaction(user_id)
        if not transaction:
            return []

        # Get list of physical info URLs
        info_urls = await self.list_physical_info(user_id, transaction.transaction_id)

        # Extract IDs from URLs and fetch each physical info
        results: list[PhysicalInformation] = []
        for url in info_urls:
            # URL format: .../physical-informations/{id}
            physical_info_id = int(url.rstrip("/").split("/")[-1])
            info = await self.get_physical_info(
                user_id, transaction.transaction_id, physical_info_id
            )
            results.append(info)

        # Commit transaction
        await self.commit_transaction(user_id, transaction.transaction_id)

        return results
