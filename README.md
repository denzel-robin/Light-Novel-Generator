
# Light Novel Generator

This project automatically creates **characters, plot outlines, and full chapters**,
allowing users to generate **complete light novels** with **custom genres and themes**.

## Features

AI-powered **character generation** with detailed backgrounds and
relationships  
Structured **plot outlines** based on user input (**genre, themes, title**)  
**Full chapter expansion** with rich descriptions and dialogues  
**Local LLM inference using Ollama** (`mistral:7b`, `aya-expanse:32b`)  
**Exports generated novels** as `.txt` files  

## Installation

### Install Ollama

Ollama is required to run AI models locally. Install it with:

```sh
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
```

### Pull an AI Model

Since command-r:35b is too large for most systems, use:

```sh
ollama pull mistral:7b
```

or

```sh
ollama pull aya-expanse:32b
```

### Clone the Repository

```sh
git clone https://github.com/denzel-robin/Light-Novel-Generator.git
cd Light-Novel-Generator
```

## Usage

Run the `main.py` file

### Example User Input

```
Enter book title: The Lost Realm
Enter book genre: Fantasy
Enter themes (comma-separated): Adventure, Magic, Betrayal
Enter number of chapters: 10
```

The AI will generate a unique novel based on your input and save it as `output/generated_novel.txt`
