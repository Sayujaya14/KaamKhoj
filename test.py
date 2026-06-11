from pymongo import MongoClient
import certifi

uri = "mongodb+srv://sharmaroy200_db_user:4pU5pyUSnTSCTYrt@cluster0.uq28jvr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(
    uri,
    tls=True,
    tlsCAFile=certifi.where()
)

print(client.admin.command("ping"))