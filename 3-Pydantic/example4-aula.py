# Este exemplo demonstra a integração do Pydantic com o FastAPI para construção de APIs. O Pydantic é utilizado para validação automática dos dados de entrada e saída das rotas HTTP, enquanto o TestClient do FastAPI é usado para testar os endpoints sem precisar subir um servidor real.
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, EmailStr, Field, field_serializer, UUID4

app = FastAPI()

# O BaseModel é a classe base do Pydantic para criar modelos de dados. Este modelo configura `extra="forbid"` para rejeitar campos desconhecidos, utiliza UUID4 como identificador único gerado automaticamente, e define um serializer customizado para converter o UUID em string ao exportar para JSON.
class User(BaseModel):
    model_config = {
        "extra": "forbid",
    }
    __users__ = []
    name: str = Field(..., description="Name of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    friends: list[UUID4] = Field(
        default_factory=list, max_items=500, description="List of friends"
    )
    blocked: list[UUID4] = Field(
        default_factory=list, max_items=500, description="List of blocked users"
    )
    signup_ts: Optional[datetime] = Field(
        default_factory=datetime.now, description="Signup timestamp", kw_only=True
    )
    id: UUID4 = Field(
        default_factory=uuid4, description="Unique identifier", kw_only=True
    )

    @field_serializer("id", when_used="json")
    def serialize_id(self, id: UUID4) -> str:
        return str(id)


# O endpoint GET /users retorna a lista de todos os usuários cadastrados em memória. O FastAPI usa o response_model para serializar e validar automaticamente a resposta com base no modelo User.
@app.get("/users", response_model=list[User])
async def get_users() -> list[User]:
    return list(User.__users__)


# O endpoint POST /users recebe os dados de um novo usuário no corpo da requisição, valida automaticamente via Pydantic e o armazena na lista em memória, retornando o usuário criado com seus campos gerados (id, signup_ts).
@app.post("/users", response_model=User)
async def create_user(user: User):
    User.__users__.append(user)
    return user


# O endpoint GET /users/{user_id} busca um usuário pelo seu UUID. Se o usuário não for encontrado, retorna uma resposta JSON com status 404 e uma mensagem de erro.
@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: UUID4) -> User | JSONResponse:
    try:
        return next((user for user in User.__users__ if user.id == user_id))
    except StopIteration:
        return JSONResponse(status_code=404, content={"message": "User not found"})


# A função main é o ponto de entrada do programa. Ela utiliza o TestClient do FastAPI para simular requisições HTTP aos endpoints, verificando criação de usuários, listagem, busca por ID e validação de dados inválidos, tudo sem necessidade de um servidor em execução.
def main() -> None:
    with TestClient(app) as client:
        for i in range(5):
            response = client.post(
                "/users",
                json={"name": f"User {i}", "email": f"example{i}@arjancodes.com"},
            )
            assert response.status_code == 200
            assert response.json()["name"] == f"User {i}", (
                "The name of the user should be User {i}"
            )
            assert response.json()["id"], "The user should have an id"

            user = User.model_validate(response.json())
            assert str(user.id) == response.json()["id"], "The id should be the same"
            assert user.signup_ts, "The signup timestamp should be set"
            assert user.friends == [], "The friends list should be empty"
            assert user.blocked == [], "The blocked list should be empty"

        response = client.get("/users")
        assert response.status_code == 200, "Response code should be 200"
        assert len(response.json()) == 5, "There should be 5 users"

        response = client.post(
            "/users", json={"name": "User 5", "email": "example5@arjancodes.com"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "User 5", (
            "The name of the user should be User 5"
        )
        assert response.json()["id"], "The user should have an id"

        user = User.model_validate(response.json())
        assert str(user.id) == response.json()["id"], "The id should be the same"
        assert user.signup_ts, "The signup timestamp should be set"
        assert user.friends == [], "The friends list should be empty"
        assert user.blocked == [], "The blocked list should be empty"

        response = client.get(f"/users/{response.json()['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "User 5", (
            "This should be the newly created user"
        )

        response = client.get(f"/users/{uuid4()}")
        assert response.status_code == 404
        assert response.json()["message"] == "User not found", (
            "We technically should not find this user"
        )

        response = client.post("/users", json={"name": "User 6", "email": "wrong"})
        assert response.status_code == 422, "The email address is should be invalid"


if __name__ == "__main__":
    main()