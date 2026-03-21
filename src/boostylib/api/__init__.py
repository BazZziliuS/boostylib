"""API endpoint modules."""

from boostylib.api.blogs import BlogsAPI
from boostylib.api.bundles import BundlesAPI
from boostylib.api.comments import CommentsAPI
from boostylib.api.donations import DonationsAPI
from boostylib.api.media import MediaAPI
from boostylib.api.posts import PostsAPI
from boostylib.api.showcase import ShowcaseAPI
from boostylib.api.subscriptions import SubscriptionsAPI
from boostylib.api.targets import TargetsAPI
from boostylib.api.users import UsersAPI

__all__ = [
    "BlogsAPI",
    "BundlesAPI",
    "CommentsAPI",
    "DonationsAPI",
    "MediaAPI",
    "PostsAPI",
    "ShowcaseAPI",
    "SubscriptionsAPI",
    "TargetsAPI",
    "UsersAPI",
]
