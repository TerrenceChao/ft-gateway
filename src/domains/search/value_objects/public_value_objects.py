from typing import List
from pydantic import BaseModel


class ContinentVO(BaseModel):
    continent_code: str
    continent_name: str


class ContinentListVO(BaseModel):
    continents: List[ContinentVO]


class CountryVO(BaseModel):
    code: str
    name: str


class CountryListVO(BaseModel):
    countries: List[CountryVO]
    continent: ContinentVO
