"""Generic pagination types used by every list query."""
from __future__ import annotations

from typing import Generic, TypeVar

import strawberry

T = TypeVar("T")


@strawberry.type
class PageInfo:
    """Metadata about the current page of results."""

    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next_page: bool
    has_previous_page: bool


@strawberry.input
class PaginationInput:
    """Pagination parameters accepted by every list query.

    Clients send `page` (1-based) and `pageSize`. The resolver translates
    to `offset` / `limit` before hitting the repository.
    """

    page: int = 1
    page_size: int = 20


def build_page_info(*, total_count: int, page: int, page_size: int) -> PageInfo:
    """Construct a PageInfo from a total row count and the current page params."""
    total_pages = max(1, -(-total_count // page_size))  # ceil division
    return PageInfo(
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next_page=page < total_pages,
        has_previous_page=page > 1,
    )


def pagination_to_offset(pagination: PaginationInput) -> tuple[int, int]:
    """Convert page-based params to (skip, limit) for repositories."""
    page = max(1, pagination.page)
    page_size = max(1, min(pagination.page_size, 100))  # cap at 100
    skip = (page - 1) * page_size
    return skip, page_size
