user_create = (
    "userdata, expected_status, expected_response_detail",
    [
        (
            {},
            422,
            {
                "detail": [
                    {
                        "input": {},
                        "loc": ["body", "email"],
                        "msg": "Field required",
                        "type": "missing",
                        "url": "https://errors.pydantic.dev/2.6/v/missing",
                    },
                    {
                        "input": {},
                        "loc": ["body", "username"],
                        "msg": "Field required",
                        "type": "missing",
                        "url": "https://errors.pydantic.dev/2.6/v/missing",
                    },
                    {
                        "input": {},
                        "loc": ["body", "password"],
                        "msg": "Field required",
                        "type": "missing",
                        "url": "https://errors.pydantic.dev/2.6/v/missing",
                    },
                ]
            },
        ),
        (
            {
                "email": "user@example.com",
                "username": "user",
                "password": "user12345",
            },
            200,
            {
                "email": "user@example.com",
                "username": "user",
            },
        ),
        (
            {
                "email": "user123",
                "username": "GRID",
                "password": "232313",
            },
            422,
            {
                "detail": [
                    {
                        "ctx": {
                            "reason": "The email address is not valid. It must have "
                            "exactly one @-sign."
                        },
                        "input": "user123",
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address: The email address is "
                        "not valid. It must have exactly one @-sign.",
                        "type": "value_error",
                    },
                    {
                        "ctx": {"min_length": 8},
                        "input": "232313",
                        "loc": ["body", "password"],
                        "msg": "String should have at least 8 characters",
                        "type": "string_too_short",
                        "url": "https://errors.pydantic.dev/2.6/v/string_too_short",
                    },
                ]
            },
        ),
        (
            {
                "email": "user@example23.com",
                "username": "User",
                "password": "user12",
            },
            422,
            {
                "detail": [
                    {
                        "ctx": {"min_length": 8},
                        "input": "user12",
                        "loc": ["body", "password"],
                        "msg": "String should have at least 8 characters",
                        "type": "string_too_short",
                        "url": "https://errors.pydantic.dev/2.6/v/string_too_short",
                    },
                ]
            },
        ),
    ],
)

user_update = (
    "user_username, userdata, expected_status, expected_response_detail",
    [
        (
            "admin",
            {
                "email": "user@user.com",
                "password": "admin1234567",
            },
            409,
            {"detail": "Email already have been taken!"},
        ),
        (
            "user",
            {
                "email": "user@yandex.ru",
                "password": "user12",
            },
            422,
            {
                "detail": [
                    {
                        "ctx": {"min_length": 8},
                        "input": "user12",
                        "loc": ["body", "password"],
                        "msg": "String should have at least 8 characters",
                        "type": "string_too_short",
                        "url": "https://errors.pydantic.dev/2.6/v/string_too_short",
                    }
                ]
            },
        ),
        (
            "moderator",
            {
                "email": "user123",
                "password": "232313",
            },
            422,
            {
                "detail": [
                    {
                        "ctx": {
                            "reason": "The email address is not valid. It must have "
                            "exactly one @-sign."
                        },
                        "input": "user123",
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address: The email address is "
                        "not valid. It must have exactly one @-sign.",
                        "type": "value_error",
                    },
                    {
                        "ctx": {"min_length": 8},
                        "input": "232313",
                        "loc": ["body", "password"],
                        "msg": "String should have at least 8 characters",
                        "type": "string_too_short",
                        "url": "https://errors.pydantic.dev/2.6/v/string_too_short",
                    },
                ]
            },
        ),
        (
            "user",
            {},
            422,
            {
                "detail": [
                    {
                        "input": {},
                        "loc": ["body", "email"],
                        "msg": "Field required",
                        "type": "missing",
                        "url": "https://errors.pydantic.dev/2.6/v/missing",
                    },
                    {
                        "input": {},
                        "loc": ["body", "password"],
                        "msg": "Field required",
                        "type": "missing",
                        "url": "https://errors.pydantic.dev/2.6/v/missing",
                    },
                ]
            },
        ),
        (
            "admin",
            {
                "email": "admin@yandex.ru",
                "password": "admin123456789",
            },
            200,
            {
                "email": "admin@yandex.ru",
                "username": "admin",
            },
        ),
    ],
)
