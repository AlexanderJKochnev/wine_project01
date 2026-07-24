# app.admin.site.py

from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_amis_admin.admin import admin
from fastapi_amis_admin.amis.components import PageSchema

from app.core.config.database.db_config import settings_db

# Create AdminSite instance
site = AdminSite(settings=Settings(database_url_async=settings_db.database_url))


# Registration management class
@site.register_admin
class GitHubIframeAdmin(admin.IframeAdmin):
    # Set page menu information
    page_schema = PageSchema(label='AmisIframeAdmin', icon='fa fa-github')
    # Set the jump link
    src = 'https://github.com/amisadmin/fastapi_amis_admin'
