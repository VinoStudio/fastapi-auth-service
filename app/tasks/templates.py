def verification_email_template(username: str, token: str) -> str:
    link = f"https://localhost:8000/auth/verify_email?token={token}&username={username}"
    payload = (
        """
    <!DOCTYPE html>
    <html>
    <title>Email</title>
    <style>
        body {
            background-color: #f0f0f2;
            color: #1e1e2a;
            font-family: Helvetica Neue, Helvetica, Arial, sans-serif;
            font-size: 12px;
            font-weight: 400;
            line-height: 14px;
            margin: 0;
            padding: 0;
        }

        h1 {
            font-size: 24px;
            font-weight: 400;
            line-height: 28px;
            margin: 0;
            padding: 0;
        }

        p {
            font-size: 14px;
            font-weight: 400;
            line-height: 20px;
            margin: 0;
            padding: 0;
        }
        .email-container {
            background-color: #ffffff;
            border: 1px solid #f0f0f2;
            border-radius: 5px;
            margin: 20px auto;
            min-width: 600px;
            min-height: 600px;
            padding: 20px;
        }
        .email-button {
            background-color: #1e1e2a;
            border-radius: 5px;
            color: #ffffff;
            display: inline-block;
            font-size: 14px;
            font-weight: 400;
            line-height: 20px;
            padding: 10px 20px;
            text-decoration: none;
            text-transform: uppercase;
        }
        
        
    </style>
    <head>
        <title>Dashboard</title>
    </head>
    <body>
    <div class="email-container">
        <h1>Dear,&nbsp;"""
        + username
        + """
        <br>
        Please, verify your email
        </h1>
        <p>Click the button below to verify your email</p>
        <br>
        <p>
            <a class="email-button" href=" """
        + link
        + """ ">
                Click to verify
            </a>
        </p>
        <br>
        <a> or click the link below to verify your email</a>
        <a href=" """
        + link
        + """ ">Verify email</a>
    </div>
    </body>
    </html>
    """
    )

    return payload
