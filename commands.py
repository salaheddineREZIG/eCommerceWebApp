from app import db

def drop_tables():
    
    db.drop_all()
    print("All tables dropped.")

if __name__ == "__main__":
    drop_tables()
