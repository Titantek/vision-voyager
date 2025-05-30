# Vision-Voyager: An Open-Ended Embodied Agent with Large Language Models

# Structure

```
vision-voyager
├── skill_library                                 <-- Skill library structure
│    ├── trial1
│    │   ├── skill
│    │   │   ├── code
│    │   │   │   ├── catchThreeFishWithCheck.js
│    │   │   │   ├── collectBamboo.js
│    │   │   │   └──  ...
│    │   │   ├── description
│    │   │   │   ├── catchThreeFishWithCheck.txt
│    │   │   │   ├── collectBamboo.txt
│    │   │   │   └── ...
│    │   │   ├── skills.json
│    │   │   └── vectordb
│    └── ...
├── voyager
│    ├── agents                                 <-- LLMs agents            
│    │   ├── action.py
│    │   ├── critic.py
│    │   ├── curriculum.py
│    │   └── skill.py
│    ├── control_primitives                     <-- Pre-defined agent control primitives
│    │   ├── craftHelper.js
│    │   ├── craftItem.js
│    │   └── ...
│    ├── │primitive_control_context
│    │   ├── craftHelper.js
│    │   ├── craftItem.js
│    │   └── ...
│    ├── env                                    <-- Python bridge with minecraft Mineflayer API
│    │   ├── mineflayer
│    │   │    ├── lib
│    │   │    ├── mineflayer-collectblock
│    │   │    ├── runs                          <-- Bot point-of-view image during the run
│    │   │    └── index.js
│    │   ├── bridge.py
│    │   ├── minecraft_launcher.py
│    │   ├── process_monitor.py
│    ├── prompts                  <--- Prompt use for LLMs
│    │   ├── action_response_format.txt
│    │   ├── action_template.txt
│    │   └── ...
│    ├── utils
│    │   ├── vision.py              <-- Manage vision
│    │   ├── json_utils.py
│    │   └── ...
├── migrate_skill_library.py    <-- Migrate skill library with new version of chromaDB
├── run.py                            <-- Script to launch the agent (Add your openai-key)
├── scitas.md                          <-- Scitas ollama setup
└── README.md
```

# Installation
Voyager requires Python ≥ 3.9 and Node.js ≥ 16.13.0. We have tested on Ubuntu 22.04. You need to follow the instructions below to install Voyager.

## Python Install
```
git clone https://github.com/MineDojo/Voyager
cd Voyager
pip install -e .
```

## Node.js Install

**WARNING**: Tested only on Ubuntu 22.04. We recommend using Ubuntu 22.04 for the best experience.

To ensure that node-canvas-webgl work (doesn't work on Windows), you can use the following command :
```
sudo apt update
sudo apt-get install -y build-essential pkg-config libx11-dev libxi-dev libxext-dev   libgl1-mesa-dev libglu1-mesa-dev libglew-dev libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev libpixman-1-dev
```

In addition to the Python dependencies, you need to install the following Node.js packages:
```
cd voyager/env/mineflayer
npm install -g npx
npm install
cd mineflayer-collectblock
npm install
npx tsc
cd ..
npm install
```

## Minecraft Instance Install

Voyager depends on Minecraft game. You need to install Minecraft game and set up a Minecraft instance.

Follow the instructions in [Minecraft Login Tutorial](installation/minecraft_instance_install.md) to set up your Minecraft Instance.

## Fabric Mods Install

You need to install fabric mods to support all the features in Voyager. Remember to use the correct Fabric version of all the mods. 

Follow the instructions in [Fabric Mods Install](installation/fabric_mods_install.md) to install the mods.

# Getting Started
Voyager uses OpenAI's GPT-4 as the language model. You need to have an OpenAI API key to use Voyager. You can get one from [here](https://platform.openai.com/account/api-keys).

After the installation process, you can run Voyager by:
```python
from voyager import Voyager

# You can also use mc_port instead of azure_login, but azure_login is highly recommended
azure_login = {
    "client_id": "YOUR_CLIENT_ID",
    "redirect_url": "https://127.0.0.1/auth-response",
    "secret_value": "[OPTIONAL] YOUR_SECRET_VALUE",
    "version": "fabric-loader-0.14.18-1.19", # the version Voyager is tested on
}
openai_api_key = "YOUR_API_KEY"

voyager = Voyager(
    azure_login=azure_login,
    openai_api_key=openai_api_key,
)

# start lifelong learning
voyager.learn()
```

* If you are running with `Azure Login` for the first time, it will ask you to follow the command line instruction to generate a config file.
* For `Azure Login`, you also need to select the world and open the world to LAN by yourself. After you run `voyager.learn()` the game will pop up soon, you need to:
  1. Select `Singleplayer` and press `Create New World`.
  2. Set Game Mode to `Creative` and Difficulty to `Peaceful`.
  3. After the world is created, press `Esc` key and press `Open to LAN`.
  4. Select `Allow cheats: ON` and press `Start LAN World`. You will see the bot join the world soon. 

# Resume from a checkpoint during learning

If you stop the learning process and want to resume from a checkpoint later, you can instantiate Voyager by:
```python
from voyager import Voyager

voyager = Voyager(
    azure_login=azure_login,
    openai_api_key=openai_api_key,
    ckpt_dir="YOUR_CKPT_DIR",
    resume=True,
)
```

# Run Voyager for a specific task with a learned skill library

If you want to run Voyager for a specific task with a learned skill library, you should first pass the skill library directory to Voyager:
```python
from voyager import Voyager

# First instantiate Voyager with skill_library_dir.
voyager = Voyager(
    azure_login=azure_login,
    openai_api_key=openai_api_key,
    skill_library_dir="./skill_library/trial1", # Load a learned skill library.
    ckpt_dir="YOUR_CKPT_DIR", # Feel free to use a new dir. Do not use the same dir as skill library because new events will still be recorded to ckpt_dir. 
    resume=False, # Do not resume from a skill library because this is not learning.
)
```
Then, you can run task decomposition. Notice: Occasionally, the task decomposition may not be logical. If you notice the printed sub-goals are flawed, you can rerun the decomposition.
```python
# Run task decomposition
task = "YOUR TASK" # e.g. "Craft a diamond pickaxe"
sub_goals = voyager.decompose_task(task=task)
```
Finally, you can run the sub-goals with the learned skill library:
```python
voyager.inference(sub_goals=sub_goals)
```

For all valid skill libraries, see [Learned Skill Libraries](skill_library/README.md).