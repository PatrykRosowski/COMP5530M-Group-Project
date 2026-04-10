from app import create_app

print("run.py: Before calling create_app()")
app = create_app()
print("run.py: After calling create_app()")

if __name__ == "__main__":
    print("run.py: Inside __main__ block, before app.run()")
    app.run(debug=True)
    print("run.py: After app.run()")