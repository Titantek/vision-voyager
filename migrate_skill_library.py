import os
import json
from pathlib import Path
from langchain_chroma.vectorstores import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_ollama.embeddings import  OllamaEmbeddings
import chromadb


def list_skill_libraries(base_path="skill_library"):
    return [f.name for f in Path(base_path).iterdir() if f.is_dir()]


def choose_from_list(prompt, options):
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    while True:
        choice = input("Enter number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("Invalid choice. Try again.")


def load_skills(skills_path):
    with open(skills_path, "r") as f:
        return json.load(f)


def regenerate_vector_db(skills, db_path, embeddings):
    if os.path.exists(db_path):
        print(f"\n🧹 Deleting existing vector DB at {db_path}...")
        os.system(f"rm -rf {db_path}")

    client = chromadb.PersistentClient(path=db_path)
    vectordb = Chroma(
        client=client,
        collection_name="skill_vectordb",
        embedding_function=embeddings,
    )

    for name, data in skills.items():
        vectordb.add_texts(
            texts=[data["description"]],
            ids=[name],
            metadatas=[{"name": name}],
        )

    print(f"✅ Regenerated {len(skills)} skills in vector DB!")


def migrate():
    print("🛠 Skill Library Vector DB Regenerator")

    base_path = "skill_library"
    libraries = list_skill_libraries(base_path)
    if not libraries:
        print("No skill libraries found.")
        return

    selected_library = choose_from_list("Select a skill library:", libraries)
    skill_dir = Path(base_path) / selected_library / "skill"
    skills_path = skill_dir / "skills.json"
    vectordb_path = skill_dir / "vectordb"

    if not skills_path.exists():
        print(f"❌ skills.json not found in {skill_dir}")
        return

    embedding_choice = choose_from_list("Choose embedding provider:", ["OpenAI", "Ollama"])
    if embedding_choice == "OpenAI":
        embeddings = OpenAIEmbeddings()
    else:
        model = input("Enter Ollama model (default: mistral): ") or "mistral"
        base_url = input("Enter Ollama base URL (default: http://localhost:5000): ") or "http://localhost:5000"
        embeddings = OllamaEmbeddings(model=model, base_url=base_url)

    skills = load_skills(skills_path)
    regenerate_vector_db(skills, str(vectordb_path), embeddings)


if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_KEY" # TODO : SET YOUR API KEY
    migrate()
