import uvicorn


if __name__ == '__main__':
    # uvicorn.run(
    #     app='Session_auth.main:session_app',
    #     host='localhost',
    #     port=8000,
    #     reload=True,
    # )

    uvicorn.run(
        app='OAuth2_auth.main:oauth2_app',
        host='localhost',
        port=8001,
        reload=True,
    )