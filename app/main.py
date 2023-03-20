from app.app import build_app


app = build_app()


if __name__ == "__main__":
    # or alternatively, run via CLI, Gunicorn, etc.
    import uvicorn
    
    uvicorn.run(app)  # type: ignore

