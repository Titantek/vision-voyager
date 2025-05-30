from voyager import Voyager
import os
import json
from pathlib import Path
from langchain_chroma.vectorstores import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_ollama.embeddings import  OllamaEmbeddings
import chromadb

openai_api_key = "YOUR_OPENAI_KEY"  # Replace with your OpenAI API key

def list_skill_libraries(base_path="skill_library"):
    return sorted([f.name for f in Path(base_path).iterdir() if f.is_dir()])


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
        print(f"\nDeleting existing vector DB at {db_path}...")
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

    print(f"Regenerated {len(skills)} skills in vector DB!")


def migrate():
    print("Skill Library Vector DB Regenerator")

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
        print(f"skills.json not found in {skill_dir}")
        return

    embedding_choice = choose_from_list("Choose embedding provider:", ["OpenAI", "Ollama"])
    if embedding_choice == "OpenAI":
        embeddings = OpenAIEmbeddings()
    else:
        model = input("Enter Ollama model (default: mistral): ") or "mistral"
        base_url = input("Enter Ollama base URL (default: http://localhost:11434): ") or "http://localhost:11434"
        embeddings = OllamaEmbeddings(model=model, base_url=base_url)

    skills = load_skills(skills_path)
    regenerate_vector_db(skills, str(vectordb_path), embeddings)


if __name__ == "__main__":

    list_of_tasks = [
    "Explore",
    "Craft a Diamond Pickaxe",
    "Craft a Golden Sword",
    "Collect a Lava Bucket",
    "Craft a Compass",
    "Build a House",
]

    list_of_models = [
        "gpt-4.1",
        "mistral-small3.1",
        "codestral",
    ]

    # User indicates minecraft port
    mc_port = int(input("Enter the Minecraft port : ") or 45595)
    # user indicates server port to use
    server_port = int(input("Enter the server port to use (default) : ") or 3000)

    # ask the user to select a task from the list
    print("Select a task from the list:")
    
    for i, task in enumerate(list_of_tasks):
        print(f"{i + 1}. {task}")
    task_choice = int(input("Enter the number of your choice: ")) - 1
    if task_choice < 0 or task_choice >= len(list_of_tasks):
        print("Invalid choice. Exiting.")
        exit(1)

    task = list_of_tasks[task_choice]
    print(f"You selected: {task}")
    # ask the user if he wants to use a skill library
    use_skill_library = input("Do you want to use a skill library? (y/n): ").strip().lower()
    if use_skill_library == 'y':
        # list the skill libraries
        libraries = list_skill_libraries()
        if not libraries:
            print("No skill libraries found.")
            exit(1)
        # ask the user to select a skill library
        for i, library in enumerate(libraries):
            print(f"{i + 1}. {library}")
        library_choice = int(input("Enter the number of your choice: ")) - 1
        if library_choice < 0 or library_choice >= len(libraries):
            print("Invalid choice. Exiting.")
            exit(1)
        selected_library = libraries[library_choice]
        print(f"You selected: {selected_library}")
    else:
        selected_library = None

    # ask the user if he wants to use vision
    use_vision = input("Do you want to use vision? (y/n): ").strip().lower()
    if use_vision == 'y':
        # ask the user to enter the path to the images
        use_vision = True
        images_path = "./voyager/env/mineflayer/runs"
        nb_images_to_use = int(input("Enter the number of images to use: ").strip())
    else:
        use_vision = False
        images_path = None
        nb_images_to_use = 0

    # User select model among the list of models for each agent
    agent_roles = [
        ("action_agent_model_name", "Action Agent"),
        ("curriculum_agent_model_name", "Curriculum Agent"),
        ("critic_agent_model_name", "Critic Agent"),
        ("skill_manager_model_name", "Skill Manager"),
        ("curriculum_agent_qa_model_name", "Curriculum Agent QA"),
    ]
    selected_models = {}
    for key, agent_name in agent_roles:
        print(f"\nSelect a model for {agent_name}:")
        for i, model in enumerate(list_of_models):
            print(f"{i + 1}. {model}")
        model_choice = int(input("Enter the number of your choice: ")) - 1
        if model_choice < 0 or model_choice >= len(list_of_models):
            print("Invalid choice. Exiting.")
            exit(1)
        selected_models[key] = list_of_models[model_choice]
    
    # set ollama to true if model is not gpt-4.1
    for key, model in selected_models.items():
        if model != "gpt-4.1":
            selected_models[key] = model
            ollama = True
        else:
            selected_models[key] = model
            ollama = False
    
    resume = input("Do you want to start from last checkpoint? (y/n): ").strip().lower()
    resume = True if resume == 'y' else False

    # create_ckpt_dir with above info take just the curriculum agent model task and vision and the selected task add also name of skill library if any
    ckpt_dir = f"ckpt_{selected_models['curriculum_agent_model_name']}_{task.replace(' ','_')}_{'vision' if use_vision else ''}_{selected_library}"

    if task != "Explore":
        max_iterations = 50
    else:
        max_iterations = 160

    # build the voyager instance with the selected models
    voyager = Voyager(
        mc_port=mc_port,
        max_iterations=max_iterations,
        openai_api_key=openai_api_key,
        server_port=server_port,
        use_vision=use_vision,
        images_path=images_path,
        nb_images_to_use=nb_images_to_use,
        ckpt_dir=ckpt_dir,
        skill_library_dir=f"./skill_library/{selected_library}" if selected_library else None,
        ollama=ollama,
        action_agent_model_name=selected_models["action_agent_model_name"],
        curriculum_agent_model_name=selected_models["curriculum_agent_model_name"],
        critic_agent_model_name=selected_models["critic_agent_model_name"],
        skill_manager_model_name=selected_models["skill_manager_model_name"],
        curriculum_agent_qa_model_name=selected_models["curriculum_agent_qa_model_name"],
        ollama_url="http://localhost:5000",
        resume=resume
    )

    if task == "Explore":
        # if the user selected "Explore", call the explore method
        voyager.learn()
    else:
        # if the user selected a task, call the inference method

        voyager.inference(task=task)

    