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
    metrica: str = Field(..., min_length=2, max_length=40, pattern=r"^[A-Za-z0-9_.\-]+$", examples=["fumaca_ppm"])
    valor: float = Field(..., ge=0.0, le=100000.0, examples=[215.5])
    temperatura_c: Optional[float] = Field(default=None, ge=-40.0, le=85.0)
    umidade_pct: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    relato: Optional[str] = Field(default="", max_length=500)
    medido_em: Optional[str] = Field(default=None, max_length=64)

    @field_validator("dispositivo_id", "metrica", mode="before")
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
    temperatura_c: Optional[float]
    umidade_pct: Optional[float]
    relato: str
    ia_sentimento: str
    ia_confianca: Optional[float]
    ia_fonte: str
    nivel_risco: Literal["normal", "atencao", "critico"]
    alerta: bool
    hash_integridade: str
    criado_em: str


class PredictIn(BaseModel):
    co_sensor_s1: float = Field(..., ge=200, le=3000, description="PT08.S1(CO) sensor response")
    c6h6_gt: float = Field(..., ge=0.1, le=80.0, description="Benzene C6H6 (ug/m3)")
    nmhc_sensor_s2: float = Field(..., ge=200, le=3000, description="PT08.S2(NMHC) sensor response")
    nox_gt: float = Field(..., ge=1.0, le=2000.0, description="NOx concentration (ppb)")
    nox_sensor_s3: float = Field(..., ge=100, le=3000, description="PT08.S3(NOx) sensor response")
    no2_gt: float = Field(..., ge=1.0, le=500.0, description="NO2 concentration (ug/m3)")
    no2_sensor_s4: float = Field(..., ge=200, le=3500, description="PT08.S4(NO2) sensor response")
    o3_sensor_s5: float = Field(..., ge=200, le=3500, description="PT08.S5(O3) sensor response")
    temperatura_c: float = Field(..., ge=-10.0, le=55.0, description="Temperature (C)")
    umidade_pct: float = Field(..., ge=5.0, le=100.0, description="Relative Humidity (%)")
    umidade_absoluta: float = Field(..., ge=0.1, le=3.5, description="Absolute Humidity (AH)")


class SimulateRequest(BaseModel):
    cenario: Literal["todos", "normal", "atencao", "critico"] = "todos"
    tipo: Literal["esp32", "drone", "app"] = "esp32"
