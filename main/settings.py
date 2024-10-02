"""
Django settings for main project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-v1jsy30^*w&5453!by)z&hi^r_p9pju1r^*le@)bclh8eua735'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*", ]


# Application definition

INSTALLED_APPS = [
    "jazzmin",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.humanize",
    "ckeditor_uploader",
    "ckeditor",
    "rest_framework",
    'rest_framework_simplejwt',
    "django_filters",
    "corsheaders",
    "drf_yasg",
    'storages',
    'location_field.apps.DefaultConfig',
    "jdatetime",
    "rangefilter",
    'import_export',
    "customadmin",
    "setting",
    "user",
    "blog",
    "service",
    "cart",
    "about",
    "contact",
    "jalali_date",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'setting.switch.SwitchMiddleware'
    
]

ROOT_URLCONF = 'main.urls'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = [
  "DELETE",
  "GET",
  "OPTIONS",
  "PATCH",
  "POST",
  "PUT",
]





TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


import os
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     os.getenv("MYSQL_DB_NAME"),
        'USER':     os.getenv("MYSQL_DB_USER"),
        'PASSWORD': os.getenv("MYSQL_DB_PASS"),
        'HOST':     os.getenv("MYSQL_DB_HOST"),
        'PORT':     os.getenv("MYSQL_DB_PORT"),
    },
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "fa-ir"

TIME_ZONE = "Asia/Tehran"

USE_I18N = True

USE_TZ = True


CKEDITOR_UPLOAD_PATH = "uploads/"


CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 300,
        "width": "100%",
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "user.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    # "user.custom_auth_backend.NumberAndOTPAuthBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        "rest_framework.authentication.SessionAuthentication",
    ),
}


STATIC_URL = "/static/"
MEDIA_URL = "/media/"


# STATIC_ROOT = BASE_DIR / "static"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(weeks=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(weeks=10),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

JAZZMIN_SETTINGS = {
    "welcome_sign": "خوش آمدید",
    "show_sidebar": True,
    "site_logo": "/images/logo.png",
    "navigation_expanded": False,
    "hide_apps": [],
    "copyright": " ",
    "hide_models": [],
    "site_title": "سینانس",
    "site_header": "سینانس",
    "related_modal_active": False,
    "icons": {
        "auth": "bi bi-people",
        "auth.Group": "bi bi-people",

        "user": "bi bi-person",
        "user.User": "bi bi-person",
        "user.UserAddress": "bi bi-geo-alt",
        "user.VisitedProduct": "bi bi-eye",

        "blog": "bi bi-book",
        "blog.ArticleCategory": "bi bi-list",
        "blog.TagArticle": "bi bi-tag",
        "blog.Article": "bi bi-book",
        "blog.CommentArticle": "bi bi-chat",

        "about": "bi bi-exclamation-circle",

        "service": "bi bi-heart-pulse",

        "contact": "bi bi-headset",

        "setting": "bi bi-gear",
        "setting.SiteSetting": "bi bi-gear",
        "setting.AboutUs": "bi bi-exclamation-circle",
        "setting.Terms": "bi bi-file-text",
        "setting.License": "bi bi-credit-card",
        "setting.Team": "bi bi-people",
        "setting.OurCustomer": "bi bi-people",
        "setting.ContactUs": "bi bi-headset",
        "setting.SettingContactUs": "bi bi-gear",
        "setting.Seller": "bi bi-people",
        "setting.SellerSocialMedia": "bi bi-instagram",
        "setting.SeoSetting": "bi bi-google",
        "setting.Feature": "bi bi-gear",
        "setting.FAQPage": "bi bi-question-circle",
        "setting.FAQ": "bi bi-question-circle",
        "setting.Banner": "bi bi-image",
        "setting.ShopBanner": "bi bi-image",
        "setting.StaticBanner": "bi bi-image",
        "setting.SocialMedia": "bi bi-instagram",
        "setting.NewsLetter": "bi bi-envelope",

        "ticket": "bi bi-ticket-perforated",
        "ticket.Ticket": "bi bi-ticket-perforated",
        "ticket.TicketSubject": "bi bi-fonts",

        "cart": "bi bi-currency-dollar",
        "cart.Cart": "bi bi-cart",
        "cart.CartItem": "bi bi-cart",
        "cart.DesignFile": "bi bi-files",
        "cart.TransferType": "bi bi-truck",
        "cart.Order": "bi bi-currency-dollar",

        "alternative_product": "bi bi-box",
        "alternative_product.Product": "bi bi-box",
        "alternative_product.ProductComment": "bi bi-chat",
        "alternative_product.Options": "bi bi-list-ul",
        "alternative_product.OptionsTitle": "bi bi-list-ul",
        "alternative_product.Gallery": "bi bi-images",
        "alternative_product.RangePrice": "bi bi-currency-dollar",
        "alternative_product.PrintPrice": "bi bi-currency-dollar",
        "alternative_product.ProductTag": "bi bi-tag",
        "alternative_product.ProductCategory": "bi bi-boxes",
        "alternative_product.ProductFAQ": "bi bi-question-circle",
        "alternative_product.Color": "bi bi-palette",
        "alternative_product.PostPrintService": "bi bi-printer",
        "alternative_product.FilterCategory": "bi bi-funnel",
        
        "analytics": "bi bi-graph-up",
        "analytics.IncomingRequest": "bi bi-graph-up",
        
        "portfolio": "bi bi-images",
        "portfolio.Portfolio": "bi bi-images",
        
        "wallet": "bi bi-wallet",
        "wallet.Wallet": "bi bi-wallet",
        "wallet.BankCard": "bi bi-credit-card",
        "wallet.WalletRequests": "bi bi-currency-exchange",
        "wallet.WalletTransactions": "bi bi-currency-exchange",

    },
}

JAZZMIN_UI_TWEAKS = {"actions_sticky_top": True}


LOCATION_FIELD = {
    "map.provider": "openstreetmap",
    "search.provider": "nominatim",
}

