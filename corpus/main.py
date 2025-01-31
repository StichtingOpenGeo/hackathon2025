from typing import List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

stop_pairs = [("Amsterdam Bijlmer Arena", "Weesp"), ("Utrecht Centraal", "Amersfoort Schothorst"), ("Maastricht", "Groningen")]

class Output(BaseModel):
    sentences: List[str] = Field(description="Voorbeeldzinnen in spreektaal gebruikt bij het ondernemen en plannen van een reis in het openbaar vervoer")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7).with_structured_output(Output)

for herkomst, bestemming in stop_pairs:
  output = llm.invoke(f"Geef voorbeeldzinnen die passen bij het plannen van een reis van {herkomst} naar {bestemming}.")
  for sentence in output.sentences:
    print(sentence)

for herkomst, bestemming in stop_pairs:
  output = llm.invoke(f"Geef voorbeeldzinnen die passen bij het reizen van {herkomst} naar {bestemming}.")
  for sentence in output.sentences:
    print(sentence)


for herkomst, bestemming in stop_pairs:
  output = llm.invoke(f"Geef voorbeeldzinnen die passen bij het reizen van {herkomst} naar {bestemming} als er problemen onderweg zijn.")
  for sentence in output.sentences:
    print(sentence)
