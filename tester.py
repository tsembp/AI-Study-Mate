response = """
Q: What is photosynthesis?
A: The process by which green plants and some other organisms convert light energy into chemical energy. Plants use sunlight, water, and carbon dioxide to produce oxygen and glucose.

Q: Define the term "mitosis"
A: A type of cell division in which a single cell divides into two identical daughter cells, each containing the same number of chromosomes as the parent cell.

Q: What is the law of conservation of energy?
A: Energy cannot be created or destroyed, only transformed from one form to another. The total amount of energy in an isolated system remains constant.
"""

flashcards = []
raw_cards = response.strip().split("\n\n")

for card in raw_cards:
    if not card.strip():
        continue
        
    parts = card.strip().split("\nA: ")
    if len(parts) != 2:
        continue
        
    question = parts[0].replace("Q: ", "").strip()
    answer = parts[1].strip()
    
    flashcards.append({
        "front": question,
        "back": answer
    })

for i, entry in enumerate(flashcards):
    print(f'Flashcard {i}')
    print(f'Front: {entry["front"]}\n')
    print(f'Back: {entry["back"]}\n')