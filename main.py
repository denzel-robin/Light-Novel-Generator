import os
import requests
import json
from dataclasses import dataclass
from typing import List, Dict, Optional, Any


@dataclass
class Character:
    name: str
    background: str
    personality: str
    goals: str
    relationships: Dict[str, str]


@dataclass
class Scene:
    content: str
    pov_character: Optional[str] = None
    location: Optional[str] = None


@dataclass
class Chapter:
    number: int
    title: str
    summary: str
    scenes: List[Scene]
    word_count: int


@dataclass
class Book:
    title: str
    genre: str
    target_audience: str
    themes: List[str]
    characters: List[Character]
    chapters: List[Chapter]
    metadata: Dict[str, Any]


class BookGenerator:
    def __init__(self, model_name: str, min_words: int, max_words: int):
        self.model_name = model_name
        self.min_words = min_words
        self.max_words = max_words
        self.base_url = "http://localhost:11434/api/generate"

    def generate_response(self, prompt: str) -> str:
        payload = {"model": self.model_name, "prompt": prompt, "stream": False}
        response = requests.post(self.base_url, json=payload)
        try:
            result = response.json()
            raw_text = result.get("response", "").strip()
            print(f"📝 AI Response:\n{raw_text}\n")  # Debugging output
            return raw_text
        except Exception as e:
            print(f"⚠️ Error parsing Ollama response: {e}")
            return ""

    def initialize_book(self, user_input: Dict) -> Book:
        return Book(
            title=user_input.get("title", "Untitled Novel"),
            genre=user_input["genre"],
            target_audience=user_input.get("target_audience", "General"),
            themes=user_input["themes"],
            characters=[],
            chapters=[],
            metadata={"created_by": "AI", "version": "1.0"},
        )

    def create_characters(
        self, genre: str, themes: List[str], title: str
    ) -> List[Character]:
        prompt = """
        Generate five unique characters for the novel with title {title}.
        Each character should have a name, background, personality traits, goals, and relationships.
        Generate the characters based on themes {themes} based on genre {genre}.
        Provide the result in JSON format example given:
        [
            {
                "name": "John Doe",
                "background": "A skilled detective in a futuristic city.",
                "personality": "Observant, witty, slightly arrogant.",
                "goals": "Solve the biggest case of his career.",
                "relationships": {"Mentor": "Old retired detective"}
            }
        ]
        """
        response = self.generate_response(prompt)

        try:
            characters = json.loads(response)
            if isinstance(characters, list):
                return [Character(**char) for char in characters]
            else:
                print("⚠️ Error: AI did not return a list.")
                return []

        except json.JSONDecodeError:
            print("Error: Failed to parse character response.")
            return []

    def create_plot_outline(
        self, num_chapters: int, genre: str, themes: List[str], title: str
    ) -> Dict:
        prompt = f"""
        Generate a structured plot outline for a {genre} novel titled "{title}" with {num_chapters} chapters.
        The novel explores the following themes: {', '.join(themes)}.
        
        Provide a short summary for each chapter in JSON format.
        Example:
        {{
            "chapters": [
                {{"chapter_number": 1, "title": "A New Beginning", "summary": "Introduce the main characters and setting."}},
                {{"chapter_number": 2, "title": "A Call to Action", "summary": "The protagonist faces their first major challenge."}}
            ]
        }}
        """

        response = self.generate_response(prompt)
        print("AI response:\n", response)
        try:
            plot = json.loads(response)
            if "chapters" in plot and isinstance(plot["chapters"], list):
                return plot
            else:
                print("⚠️ Error: AI did not return a valid chapters list.")
                return {"chapters": []}

        except json.JSONDecodeError:
            print("Error: Failed to parse Ollama response.")
            return {"chapters": []}

    def generate_chapter(self, chapter_number: int, chapter_summary: str) -> Chapter:
        if not chapter_summary:
            print(f"⚠️ Skipping Chapter {chapter_number}: No summary available.")
            return Chapter(
                number=0,
                title="",
                summary="",
                scenes=[Scene(content="")],
                word_count=0,
            )

        prompt = f"""
        Expand the following chapter summary into a detailed chapter with rich descriptions, dialogues, and scene transitions.
        Ensure the writing style is engaging and fits the novel's genre.
        Chapter {chapter_number} Summary: {chapter_summary}
        """
        content = self.generate_response(prompt)
        return Chapter(
            number=chapter_number,
            title=f"Chapter {chapter_number}",
            summary=chapter_summary,
            scenes=[Scene(content=content)],
            word_count=len(content.split()),
        )

    def export_book(self, book: Book, output_dir: str) -> str:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = os.path.join(output_dir, "generated_novel.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Title: {book.title}\n")
            f.write(f"Genre: {book.genre}\n")
            f.write(f"Themes: {', '.join(book.themes)}\n\n")

            for chapter in book.chapters:
                f.write(f"Chapter {chapter.number}: {chapter.title}\n")
                f.write(f"{chapter.summary}\n\n")
                for scene in chapter.scenes:
                    f.write(scene.content + "\n\n")

        return output_path


def get_user_input() -> Dict:
    title = input("Enter book title: ")
    genre = input("Enter book genre: ")
    themes = input("Enter themes (comma-separated): ").split(",")
    num_chapters = int(input("Enter number of chapters: "))

    return {
        "title": title,
        "genre": genre,
        "themes": themes,
        "num_chapters": num_chapters,
    }


def main():
    user_input = get_user_input()
    generator = BookGenerator(model_name="mistral:7b", min_words=800, max_words=2000)

    book = generator.initialize_book(user_input)
    book.characters = generator.create_characters(
        user_input["genre"], user_input["themes"], user_input["title"]
    )
    plot = generator.create_plot_outline(
        user_input["num_chapters"],
        user_input["genre"],
        user_input["themes"],
        user_input["title"],
    )

    if not plot["chapters"]:
        print("⚠️ No chapters were generated. Exiting.")
        return

    for i in range(user_input["num_chapters"]):
        chapter = generator.generate_chapter(i + 1, plot["chapters"][i]["summary"])
        book.chapters.append(chapter)

    output_path = generator.export_book(book, "output")
    print(f"Book saved to: {output_path}")


main()
