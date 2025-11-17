from langchain_huggingface import HuggingFaceEmbeddings

print("Downloading embedding model...")
embedding = HuggingFaceEmbeddings(model="intfloat/multilingual-e5-base")
print("Model downloaded successfully.")
