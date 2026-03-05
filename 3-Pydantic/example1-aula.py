# O Pydantic é uma biblioteca de validação de dados e criação de modelos de dados em Python. Ele é amplamente utilizado para garantir que os dados de entrada estejam no formato correto e para criar modelos de dados robustos que podem ser facilmente manipulados.
from enum import auto, IntFlag
from typing import Any
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
    ValidationError,
)

# O IntFlag é uma classe de enumeração que permite criar conjuntos de flags usando operadores bit a bit. Ele é útil para representar combinações de opções ou permissões.
class Role(IntFlag):
    Author = auto()
    Editor = auto()
    Developer = auto()
    Admin = Author | Editor | Developer

# O BaseModel é a classe base para criar modelos de dados no Pydantic. Ele fornece funcionalidades de validação e serialização de dados.
class User(BaseModel):
    name: str = Field(examples=["Arjan"])
    email: EmailStr = Field(
        examples=["example@arjancodes.com"],
        description="The email address of the user",
        frozen=True,
    )
    password: SecretStr = Field(
        examples=["Password123"], description="The password of the user"
    )
    role: Role = Field(default=None, description="The role of the user")

# A função validate é responsável por validar os dados de entrada usando o modelo User. Ela tenta criar uma instância do modelo com os dados fornecidos e, se ocorrer um erro de validação, ela captura a exceção e imprime os erros.
def validate(data: dict[str, Any]) -> None:
    try:
        user = User.model_validate(data)
        print(user)
    except ValidationError as e:
        print("User is invalid")
        for error in e.errors():
            print(error)

# A função main é o ponto de entrada do programa. Ela define dois conjuntos de dados, um válido e outro inválido, e chama a função validate para cada um deles. Casos de teste são usados para demonstrar a validação de dados usando o Pydantic.
def main() -> None:
    good_data = {
        "name": "Arjan",
        "email": "example@arjancodes.com",
        "password": "Password123",
    }
    bad_data = {"email": "<bad data>", "password": "<bad data>"}

    validate(good_data)
    validate(bad_data)


if __name__ == "__main__":
    main()