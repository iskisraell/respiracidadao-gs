from typing import Literal, Optional
from pydantic import AliasChoices, BaseModel, Field, field_validator


class OcorrenciaIn(BaseModel):
    dispositivo_id: str = Field(..., min_length=2, max_length=64, pattern=r"^[A-Za-z0-9_.:\-]+$", examples=["esp32-respira-01"])
    tipo: Literal["esp32", "drone", "app"] = Field(
        default="esp32",
        validation_alias=AliasChoices("tipo", "tipo_dispositivo"),
    )
    latitude: Optional[float] = Field(default=-23.5641, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(default=-46.6524, ge=-180.0, le=180.0)
    metrica: Literal["gas_voc", "gas_co"] = Field(default="gas_voc", description="Sensor que define o risco local (o mesmo do LED do ESP32)")
    valor: float = Field(..., ge=0.0, le=100000.0, examples=[1180.0])
    gas_co: Optional[float] = Field(default=None, ge=0.0, le=5000.0, examples=[1290.0])
    temperatura_c: Optional[float] = Field(default=None, ge=-40.0, le=85.0)
    umidade_pct: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    relato: Optional[str] = Field(default="", max_length=500)
    medido_em: Optional[str] = Field(default=None, max_length=64)

    @field_validator("dispositivo_id", mode="before")
    @classmethod
    def strip_clean(cls, v):
        if not isinstance(v, str):
            return v
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Campo obrigatório não pode ser vazio.")
        return cleaned


class OcorrenciaOut(BaseModel):
    id: int
    dispositivo_id: str
    tipo: str
    latitude: Optional[float]
    longitude: Optional[float]
    metrica: str
    valor: float
    gas_co: Optional[float]
    temperatura_c: Optional[float]
    umidade_pct: Optional[float]
    relato: str
    ia_sentimento: str
    ia_confianca: Optional[float]
    ia_fonte: str
    nivel_risco: Literal["normal", "atencao", "critico"]
    alerta: bool
    ia_risco: Optional[str]
    ia_risco_prob: Optional[float]
    hash_integridade: str
    criado_em: str


class PredictIn(BaseModel):
    """As 4 leituras do ESP32, na mesma escala dos sensores MOx da base UCI."""

    gas_co: float = Field(..., ge=400, le=2500, description="Indice do sensor de CO (MQ-7 / PT08.S1)")
    gas_voc: float = Field(..., ge=300, le=2500, description="Indice do sensor de gases/fumaca (MQ-135 / PT08.S2)")
    temperatura_c: float = Field(..., ge=-10.0, le=55.0)
    umidade_pct: float = Field(..., ge=5.0, le=100.0)


class SimulateRequest(BaseModel):
    cenario: Literal["todos", "normal", "atencao", "critico"] = "todos"
    tipo: Literal["esp32", "drone", "app"] = "esp32"
