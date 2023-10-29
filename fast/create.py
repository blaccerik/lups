from utils.database import engine

if __name__ == '__main__':
    print(Base.metadata)
    Base.metadata.create_all(bind=engine)