# Import all models so Alembic can detect them
from app.models.user import User
from app.models.affiliate_profile import AffiliateProfile
from app.models.store import Store
from app.models.product import Product
from app.models.campaign import Campaign
from app.models.referral_link import ReferralLink
from app.models.referral_click import ReferralClick
from app.models.conversion import Conversion
from app.models.affiliate_balance import AffiliateBalance
from app.models.payout_request import PayoutRequest
from app.models.platform_setting import PlatformSetting
from app.models.creative_asset import CreativeAsset
from app.models.notification import Notification
