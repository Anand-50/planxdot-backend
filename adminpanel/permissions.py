ROLE_PERMISSIONS = {
    "super_admin": ["*"],

    "operations_admin": [
        "USER_SUSPEND",
        "SUBSCRIPTION_EXTEND",
        "POST_STATUS"
    ],

    "fraud_team": [
        "USER_SUSPEND",
        "CHAT_FREEZE",
        "VIEW_NDA"
    ],

    "support": [
        "SUBSCRIPTION_EXTEND"
    ],

    "moderator": [
        "POST_STATUS",
        "VIEW_NDA"
    ],

    "ads_manager": [],

    "analytics": []
}
