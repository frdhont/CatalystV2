from app import db
from catalyst.reporting.data_cleaning import create_cerberus_validation_dict, generate_cerberus_data_issues, generate_data_issues
from catalyst.loadfiles.source_data import get_source_data
import config
import pandas as pd
from cerberus import Validator
import json
from catalyst.loadfiles import get_loadfile
from catalyst.models import Entity, ParameterQuery, GoLive
from app import db
import pytest
#from pytest import TestC
from catalyst import create_task, process_all_tasks
from catalyst.loadfiles import mapping
from datetime import datetime
from msal import PublicClientApplication

app = PublicClientApplication(
    "your_client_id",
    authority="https://login.microsoftonline.com/4f45513a-0e45-4d2d-be0a-4b3d8738b3b1")
result = None  # It is just an initial value. Please follow instructions below.

# We now check the cache to see
# whether we already have some accounts that the end user already used to sign in before.
accounts = app.get_accounts()
if accounts:
    # If so, you could then somehow display these accounts and let end user choose
    print("Pick the account you want to use to proceed:")
    for a in accounts:
        print(a["username"])
    # Assuming the end user chose this one
    chosen = accounts[0]
    # Now let's try to find a token in cache for this account
    result = app.acquire_token_silent(["your_scope"], account=chosen)

if not result:
    # So no suitable token exists in cache. Let's get a new one from Azure AD.
    result = app.acquire_token_by_one_of_the_actual_method(..., scopes=["User.Read"])
if "access_token" in result:
    print(result["access_token"])  # Yay!
else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You may need this when reporting a bug

"""
# x =
data = df.apply(lambda id: id + '0')

print(data)
"""