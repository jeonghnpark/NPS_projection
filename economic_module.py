import numpy as np
import pandas as pd


class EconomicModule:
    def __init__(self):
        """경제모듈 초기화"""
        self.params = {
            "gdp_growth_rate": {  # 실질 GDP 성장률
                2023: 0.022,  # 2.2%
                2030: 0.019,  # 1.9%
                2040: 0.013,  # 1.3%
                2050: 0.008,  # 0.8%
                2060: 0.007,  # 0.7%
                2070: 0.007,  # 0.7%
            },
            "wage_growth_rate": {  # 실질임금상승률
                2023: 0.023,  # 2.3%
                2030: 0.020,  # 2.0%
                2040: 0.018,  # 1.8%
                2050: 0.016,  # 1.6%
                2060: 0.015,  # 1.5%
                2070: 0.015,  # 1.5%
            },
            "inflation_rate": {  # 물가상승률 (보고서 p.12 참조)
                2023: 0.033,  # 3.3%
                2024: 0.028,  # 2.8%
                2025: 0.024,  # 2.4%
                2026: 0.022,  # 2.2%
                2027: 0.020,  # 2.0%
                2030: 0.020,  # 2.0%
                2040: 0.020,  # 2.0%
                2050: 0.020,  # 2.0%
                2060: 0.020,  # 2.0%
            },
            "nominal_wage_growth_rate": {  # 명목임금상승률
                2023: 0.047,  # 4.7%
                2030: 0.044,  # 4.4%
                2040: 0.042,  # 4.2%
                2050: 0.040,  # 4.0%
                2060: 0.039,  # 3.9%
            },
        }

        # 기준연도(2023) 경제지표
        self.base_values = {
            "nominal_gdp": 2100e12,  # 2023년 명목 GDP (2100조원)
            "nominal_wage": 3.85e6,  # 2023년 월평균 임금 (385만원)
        }

    def project_variables(self, year):
        """특정 연도의 경제변수 추계"""
        # 1. 성장률 추계
        gdp_growth = self._get_gdp_growth_rate(year)
        real_wage_growth = self._get_wage_growth_rate(year)
        inflation = self._get_inflation_rate(year)
        nominal_wage_growth = self._get_nominal_wage_growth_rate(year)

        # 2. GDP 추계 (실질, 명목)
        real_gdp = self._calculate_real_gdp(year)
        nominal_gdp = self._calculate_nominal_gdp(year)

        # 3. 임금 추계 (실질, 명목)
        real_wage = self._calculate_real_wage(year)
        nominal_wage = self._calculate_nominal_wage(year)

        return {
            "year": year,
            "gdp_growth_rate": gdp_growth,
            "real_wage_growth_rate": real_wage_growth,
            "inflation_rate": inflation,
            "nominal_wage_growth_rate": nominal_wage_growth,
            "real_gdp": real_gdp,
            "nominal_gdp": nominal_gdp,
            "real_wage": real_wage,
            "nominal_wage": nominal_wage,
        }

    def _get_gdp_growth_rate(self, year):
        """특정 연도의 실질 GDP 성장률 반환"""
        years = sorted(self.params["gdp_growth_rate"].keys())
        rates = [self.params["gdp_growth_rate"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        return np.interp(year, years, rates)

    def _get_wage_growth_rate(self, year):
        """특정 연도의 실질임금상승률 반환"""
        years = sorted(self.params["wage_growth_rate"].keys())
        rates = [self.params["wage_growth_rate"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        return np.interp(year, years, rates)

    def _get_inflation_rate(self, year):
        """특정 연도의 물가상승률 반환"""
        years = sorted(self.params["inflation_rate"].keys())
        rates = [self.params["inflation_rate"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        return np.interp(year, years, rates)

    def _get_nominal_wage_growth_rate(self, year):
        """특정 연도의 명목임금상승률 반환"""
        years = sorted(self.params["nominal_wage_growth_rate"].keys())
        rates = [self.params["nominal_wage_growth_rate"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        return np.interp(year, years, rates)

    def _calculate_real_gdp(self, year):
        """실질 GDP 계산"""
        base_year = 2023
        real_gdp = self.base_values["nominal_gdp"]

        for y in range(base_year + 1, year + 1):
            growth_rate = self._get_gdp_growth_rate(y)
            real_gdp *= 1 + growth_rate

        return real_gdp

    def _calculate_nominal_gdp(self, year):
        """명목 GDP 계산"""
        real_gdp = self._calculate_real_gdp(year)
        base_year = 2023
        inflation_factor = 1.0

        for y in range(base_year + 1, year + 1):
            inflation_rate = self._get_inflation_rate(y)
            inflation_factor *= 1 + inflation_rate

        return real_gdp * inflation_factor

    def _calculate_real_wage(self, year):
        """실질임금 계산"""
        base_year = 2023
        real_wage = self.base_values["nominal_wage"]

        for y in range(base_year + 1, year + 1):
            growth_rate = self._get_wage_growth_rate(y)
            real_wage *= 1 + growth_rate

        return real_wage

    def _calculate_nominal_wage(self, year):
        """명목임금 계산"""
        base_year = 2023
        nominal_wage = self.base_values["nominal_wage"]

        for y in range(base_year + 1, year + 1):
            growth_rate = self._get_nominal_wage_growth_rate(y)
            nominal_wage *= 1 + growth_rate

        return nominal_wage
