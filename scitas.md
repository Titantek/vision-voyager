# Setup scitas ollama job

## Pull docker image

Pull image in the `myimages` directory. You can change the path to your own directory.

```bash
`apptainer pull ollama.sif docker://ollama/ollama`

## Create a new scitas job

`submit_ollama.run` is a script that will run the docker image. You can modify the parameters in the script to suit your needs. 

```bash
#!/bin/bash

#SBATCH --job-name=ollama
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 8
#SBATCH --mem 16G CHANGE MEMORY IF NEEDED
#SBATCH --gres=gpu:1
#SBATCH --time 05:00:00 CHANGE TIME IF NEEDED
#SBATCH --output=./logs/slurm-%j.out
#SBATCH --account=cs-503
#SBATCH --qos=cs-503

sleep infinity
```

## Run the job
```bash
sbatch submit_ollama.run
```

## Connect to the job

`squeue -u $USER` to get the job ID.

```bash
srun --pty --jobid <JOBID> /bin/bash
```

## Start tmux session
```bash
module load tmux
tmux new -s ollama
```

## start container
```bash
apptainer shell --nv \
   --bind /home/<user>/ollama_models:/root/.ollama \
   /home/<user>/myimages/ollama.sif
```

## Start the server
```bash
export OLLAMA_HOST=0.0.0.0:11434
ollama serve
```

## detaching from tmux
```bash
Ctrl+b -> d
```

## pull models
Detach from the tmux session and run the following command to pull the model.

```bash
apptainer exec --bind /home/<user>/ollama_models:/root/.ollama /home/<user>/myimages/ollama.sif ollama pull <MODEL_NAME>
```

## Node IP

To get the node IP, run the following command in the tmux session.

```bash
hostname -i
```

## check olllama server
reconnect to the tmux session
```bash
tmux attach -t ollama
```

## Port forwarding
To access the server from your local machine, you need to set up port forwarding. You can do this using SSH. Replace `<local_port>` with the port you want to use on your local machine, `<node_ip>` with the node ID you got from `hostname -i`, and `<host_port>` with the port you used in `export OLLAMA_HOST`.
```bash
ssh -L <local_port>:10.91.27.<X>:<host_port> -l <user> izar.epfl.ch -f -N
```

