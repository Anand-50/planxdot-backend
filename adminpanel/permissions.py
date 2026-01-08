ROLE_PERMISSIONS = {
    "super_admin": ["*"],

    "operations_admin": [
        "VIEW_DASHBOARD",
        "VIEW_ANALYTICS",     
        "USER_SUSPEND",
        "SUBSCRIPTION_EXTEND",
        "POST_STATUS",
        "VIEW_REPORTS"
    ],

    "fraud_team": [
        "VIEW_REPORTS",
        "MANAGE_REPORTS",
        "USER_SUSPEND",
        "CHAT_FREEZE"
    ],

    "support": [
        "SUBSCRIPTION_EXTEND"
    ],

    "moderator": [
        "VIEW_REPORTS",
        "MANAGE_REPORTS",
        "POST_STATUS"
    ],

    "ads_manager": [
        "VIEW_ANALYTICS"  
    ],

    "analytics": [
        "VIEW_DASHBOARD",
        "VIEW_ANALYTICS"     
    ],
}



def require_permission(admin, permission):
    allowed = ROLE_PERMISSIONS.get(admin.role, [])

    if "*" in allowed:
        return

    if permission not in allowed:
        raise Exception("Permission denied")