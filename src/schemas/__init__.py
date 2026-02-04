"""
Schemas Package
"""
from .blog import (
    BlogImageCreate,
    BlogImageResponse,
    BlogPostCreate,
    BlogPostUpdate,
    BlogPostResponse,
    BlogPostListResponse,
    MarkdownFileCreate,
    MarkdownFileUpdate,
    MarkdownFileResponse,
    PostMetadata,
    MetadataUpdate,
    MetadataResponse,
    AIContentRequest,
    BlogNewPostRequest,
)

from .hrjang import (
    HrCommentCreate,
    HrCommentDelete,
    HrCommentResponse,
    HrCommentListResponse,
)

from .hskmap import (
    HSKRequest,
    HSKResponse,
)

from .lawchaser import (
    LawListRequest,
    LawOldNewRequest,
    ArticleCherserRequest,
    LawListResponse,
    LawOldNewResponse,
    ArticleResponse,
)

from .rara import (
    RaraBasicRequest,
    RaraCustomRequest,
    RaraRatingRequest,
    RaraSurveyRequest,
    RaraBasicResponse,
    RaraCustomResponse,
    RaraModelResponse,
    SuccessResponse,
)

__all__ = [
    # Blog
    "BlogImageCreate",
    "BlogImageResponse",
    "BlogPostCreate",
    "BlogPostUpdate",
    "BlogPostResponse",
    "BlogPostListResponse",
    "MarkdownFileCreate",
    "MarkdownFileUpdate",
    "MarkdownFileResponse",
    "PostMetadata",
    "MetadataUpdate",
    "MetadataResponse",
    "AIContentRequest",
    "BlogNewPostRequest",
    # HRJang
    "HrCommentCreate",
    "HrCommentDelete",
    "HrCommentResponse",
    "HrCommentListResponse",
    # HSKMap
    "HSKRequest",
    "HSKResponse",
    # LawChaser
    "LawListRequest",
    "LawOldNewRequest",
    "ArticleCherserRequest",
    "LawListResponse",
    "LawOldNewResponse",
    "ArticleResponse",
    # Rara
    "RaraBasicRequest",
    "RaraCustomRequest",
    "RaraRatingRequest",
    "RaraSurveyRequest",
    "RaraBasicResponse",
    "RaraCustomResponse",
    "RaraModelResponse",
    "SuccessResponse",
]
