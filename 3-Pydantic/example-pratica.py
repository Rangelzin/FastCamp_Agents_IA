# Prática Pydantic — exemplos 1 ao 4 de forma resumida
import enum
import hashlib
import re
from datetime import datetime
from typing import Any, Optional, Self
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import (
    BaseModel, EmailStr, Field, SecretStr, UUID4, ValidationError,
    field_serializer, field_validator, model_serializer, model_validator,
)

VALID_PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")

# ── Ex1: modelo básico — tipos nativos do Pydantic ──────────────────────────
class Role(enum.IntFlag):
    Author = 1; Editor = 2; Admin = 4; SuperAdmin = 8

class UsuarioBasico(BaseModel):
    name: str
    email: EmailStr
    password: SecretStr
    role: Role = Field(default=None)

# ── Ex2: field_validator + model_validator ───────────────────────────────────
# model_validator(before) valida antes de criar a instância (regras cruzadas).
# field_validator valida campos individualmente.
class UsuarioValidado(BaseModel):
    name: str
    email: EmailStr = Field(frozen=True)
    password: SecretStr
    role: Role = Field(default=None)

    @field_validator("name")
    @classmethod
    def validar_nome(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z]{2,}$", v):
            raise ValueError("Nome inválido: só letras, mínimo 2 caracteres")
        return v

    @field_validator("role", mode="before")
    @classmethod
    def validar_role(cls, v: int | str | Role) -> Role:
        try:
            return Role(v) if isinstance(v, int) else Role[v]
        except (KeyError, ValueError):
            raise ValueError(f"Role inválido. Use: {', '.join(r.name for r in Role)}")

    @model_validator(mode="before")
    @classmethod
    def validar_usuario(cls, v: dict[str, Any]) -> dict[str, Any]:
        if not VALID_PASSWORD_RE.match(v.get("password", "")):
            raise ValueError("Senha fraca: mínimo 8 chars, 1 maiúscula, 1 minúscula, 1 número")
        if v.get("name", "").casefold() in v["password"].casefold():
            raise ValueError("Senha não pode conter o nome")
        v["password"] = hashlib.sha256(v["password"].encode()).hexdigest()
        return v

# ── Ex3: field_serializer + model_serializer ─────────────────────────────────
# field_serializer controla como um campo é exportado para JSON.
# model_serializer controla a saída completa do modelo ao serializar.
class RoleCompleto(enum.IntFlag):
    User = 0; Author = 1; Editor = 2; Admin = 4; SuperAdmin = 8

class UsuarioSerializado(BaseModel):
    name: str
    email: EmailStr = Field(frozen=True)
    password: SecretStr = Field(exclude=True)  # nunca exposta
    role: RoleCompleto = Field(default=0, validate_default=True)

    @model_validator(mode="before")
    @classmethod
    def validar(cls, v: dict[str, Any]) -> dict[str, Any]:
        if not VALID_PASSWORD_RE.match(v.get("password", "")):
            raise ValueError("Senha inválida.")
        v["password"] = hashlib.sha256(v["password"].encode()).hexdigest()
        return v

    @model_validator(mode="after")
    def so_arjan_admin(self, _: Any) -> Self:
        if self.role == RoleCompleto.Admin and self.name != "Arjan":
            raise ValueError("Apenas Arjan pode ser Admin")
        return self

    @field_serializer("role", when_used="json")
    @classmethod
    def ser_role(cls, v: RoleCompleto) -> str:
        return v.name

    @model_serializer(mode="wrap", when_used="json")
    def ser_usuario(self, serializer, info) -> dict[str, Any]:
        if not info.include and not info.exclude:
            return {"name": self.name, "role": self.role.name}
        return serializer(self)

# ── Ex4: integração FastAPI + TestClient ─────────────────────────────────────
# O FastAPI usa o Pydantic para validar entrada/saída automaticamente.
# extra="forbid" rejeita campos desconhecidos; UUID4 gera id único.
app = FastAPI()
_db: list = []

class UsuarioAPI(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    email: EmailStr
    id: UUID4 = Field(default_factory=uuid4, kw_only=True)
    signup_ts: Optional[datetime] = Field(default_factory=datetime.now, kw_only=True)

    @field_serializer("id", when_used="json")
    def ser_id(self, id: UUID4) -> str:
        return str(id)

@app.get("/users", response_model=list[UsuarioAPI])
async def listar() -> list[UsuarioAPI]:
    return list(_db)

@app.post("/users", response_model=UsuarioAPI)
async def criar(user: UsuarioAPI):
    _db.append(user); return user

@app.get("/users/{user_id}", response_model=UsuarioAPI)
async def buscar(user_id: UUID4) -> UsuarioAPI | JSONResponse:
    try:
        return next(u for u in _db if u.id == user_id)
    except StopIteration:
        return JSONResponse(status_code=404, content={"message": "Não encontrado"})

# ── Main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    # Ex1 — modelo básico
    u1 = UsuarioBasico.model_validate({"name": "Arjan", "email": "a@a.com", "password": "abc"})
    print("Ex1:", u1.name, u1.email)

    # Ex2 — validadores
    try:
        UsuarioValidado.model_validate({"name": "Arjan", "email": "a@a.com", "password": "fraca"})
    except ValidationError as e:
        print("Ex2 erro:", e.errors()[0]["msg"])

    # Ex3 — serialização
    u3 = UsuarioSerializado.model_validate(
        {"name": "Arjan", "email": "a@a.com", "password": "Senha@123", "role": "Admin"}
    )
    print("Ex3 json:", u3.model_dump(mode="json"))

    # Ex4 — FastAPI
    with TestClient(app) as client:
        r = client.post("/users", json={"name": "João", "email": "joao@a.com"})
        uid = r.json()["id"]
        print("Ex4 criado:", r.json()["name"], uid[:8] + "...")
        r2 = client.get(f"/users/{uid}")
        print("Ex4 buscado:", r2.json()["name"])


if __name__ == "__main__":
    main()
