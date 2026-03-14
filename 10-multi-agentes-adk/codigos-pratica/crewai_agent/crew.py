# crew.py
from crewai import Crew, Process
from agents_and_tasks import researcher, calculator, research_task, calculation_task

crew = Crew(
    agents=[researcher, calculator],
    tasks=[research_task, calculation_task],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    planeta = input("Digite o nome do planeta: ")
    massa = input("Digite sua massa em kg: ")

    result = crew.kickoff(inputs={
        "planeta": planeta,
        "massa": massa
    })

    print("\n========== RESULTADO ==========")
    print(result)